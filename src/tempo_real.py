"""Detecção de barreiras de calçada em tempo real (webcam, celular ou vídeo).

Desenha as caixas, mede o FPS e marca no chão uma "zona de caminhada" (o trecho
logo à frente de quem anda). Quando uma barreira entra nessa zona, a zona fica
vermelha e aparece o aviso na tela, como um alerta em realidade aumentada.

Exemplos (no Windows, use py no lugar de python):
  # webcam do computador
  python src/tempo_real.py --modelo modelos/best.pt --fonte 0

  # câmera do celular pelo app DroidCam, na mesma rede Wi-Fi (o app mostra o IP)
  python src/tempo_real.py --modelo modelos/best.pt --fonte http://IP-DO-CELULAR:4747/video --rastrear

  # vídeo gravado andando na calçada, contando as barreiras e salvando o resultado
  python src/tempo_real.py --modelo modelos/best.pt --fonte caminhada.mp4 --rastrear --salvar resultados/demo.mp4

Em fonte ao vivo (câmera ou URL), uma thread lê a câmera o tempo todo e o modelo
sempre recebe o quadro mais recente: se o modelo for mais lento que a câmera, os
quadros velhos são descartados em vez de formar fila, e o atraso não cresce. Com
--salvar, o vídeo ao vivo é gravado com o FPS medido, para tocar na velocidade real.
Em vídeo gravado, todos os quadros são processados, na ordem.

Teclas: q ou Esc para sair.
"""
from __future__ import annotations

import argparse
import threading
import time
from collections import Counter, deque

import cv2
import numpy as np

# cores BGR por classe; classes que não estiverem aqui saem em branco
CORES = {
    "buraco": (36, 28, 237),            # vermelho
    "desnivel": (0, 140, 255),          # laranja
    "obstaculo": (0, 215, 255),         # amarelo
    "veiculo_na_calcada": (255, 144, 30),  # azul
    "dano_no_piso": (36, 28, 237),      # vermelho (modelo de 2 classes: buraco + desnível)
}
# como cada classe aparece na tela (o OpenCV não desenha acentos)
NOME_NA_TELA = {"dano_no_piso": "dano no piso", "veiculo_na_calcada": "veiculo na calcada"}
VERDE = (80, 175, 76)
VERMELHO = (36, 28, 237)


class LeitorAoVivo:
    """Lê uma fonte ao vivo numa thread e guarda só o quadro mais recente."""

    def __init__(self, cap) -> None:
        self.cap = cap
        self._quadro = None
        self._numero = 0          # quantos quadros a câmera já entregou
        self._entregue = 0        # número do último quadro passado ao modelo
        self._usados = 0          # quantos quadros o modelo recebeu
        self._fim = False
        self._parar = False
        self._trava = threading.Condition()
        self._thread = threading.Thread(target=self._ler, daemon=True)
        self._thread.start()

    def _ler(self) -> None:
        while not self._parar:
            ok, quadro = self.cap.read()
            with self._trava:
                if not ok:
                    self._fim = True
                    self._trava.notify_all()
                    return
                self._quadro, self._numero = quadro, self._numero + 1
                self._trava.notify_all()

    def read(self, espera: float = 5.0):
        """Devolve (ok, quadro) com um quadro mais novo que o último entregue."""
        with self._trava:
            self._trava.wait_for(lambda: self._numero > self._entregue or self._fim, timeout=espera)
            if self._numero > self._entregue:
                self._entregue = self._numero
                self._usados += 1
                return True, self._quadro
            return False, None

    @property
    def descartados(self) -> int:
        """Quadros que a câmera entregou e o modelo não chegou a ver."""
        return self._numero - self._usados

    def release(self) -> None:
        self._parar = True
        self._thread.join(timeout=1.0)
        self.cap.release()


def abrir_gravador(caminho: str, fps: float, w: int, h: int) -> cv2.VideoWriter:
    return cv2.VideoWriter(caminho, cv2.VideoWriter_fourcc(*"mp4v"), max(1.0, fps), (w, h))


def eh_ao_vivo(fonte) -> bool:
    return isinstance(fonte, int) or str(fonte).lower().startswith(("http://", "https://", "rtsp://", "rtmp://"))


def argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detector de barreiras do Passo Firme em tempo real")
    p.add_argument("--modelo", default="modelos/best.pt", help="pesos treinados (best.pt)")
    p.add_argument("--fonte", default="0", help="0 = webcam; URL de stream; ou caminho de vídeo")
    p.add_argument("--conf", type=float, default=0.35, help="confiança mínima para mostrar uma caixa")
    p.add_argument("--imgsz", type=int, default=640, help="tamanho de entrada do modelo")
    p.add_argument("--rastrear", action="store_true", help="dá um ID a cada barreira e conta as distintas")
    p.add_argument("--salvar", default="", help="caminho .mp4 para gravar o vídeo anotado")
    p.add_argument("--sem-janela", action="store_true", help="não abre janela (útil em servidor)")
    return p.parse_args()


def zona_de_caminhada(w: int, h: int, base: float = 0.70, topo: float = 0.30, altura: float = 0.45) -> np.ndarray:
    """Trapézio na parte de baixo da imagem: o chão logo à frente de quem caminha."""
    y_topo = int(h * (1 - altura))
    return np.array(
        [
            [int(w * (1 - base) / 2), h - 1],
            [int(w * (1 + base) / 2), h - 1],
            [int(w * (1 + topo) / 2), y_topo],
            [int(w * (1 - topo) / 2), y_topo],
        ],
        dtype=np.int32,
    )


def na_zona(zona: np.ndarray, x: float, y: float) -> bool:
    return cv2.pointPolygonTest(zona, (float(x), float(y)), False) >= 0


def escrever(img: np.ndarray, texto: str, org: tuple[int, int], cor=(255, 255, 255), escala: float = 0.6) -> None:
    """Texto com fundo escuro, legível em qualquer cena. Use só ASCII (o OpenCV não desenha acentos)."""
    (tw, th), base = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, 2)
    x, y = org
    cv2.rectangle(img, (x - 4, y - th - 6), (x + tw + 4, y + base), (0, 0, 0), -1)
    cv2.putText(img, texto, (x, y - 2), cv2.FONT_HERSHEY_SIMPLEX, escala, cor, 2, cv2.LINE_AA)


def desenhar(frame: np.ndarray, caixas: list[dict], zona: np.ndarray) -> tuple[str, float] | None:
    """Desenha caixas e zona; devolve (classe, confiança) da barreira mais confiável dentro da zona."""
    alerta = None
    for c in caixas:
        x1, y1, x2, y2 = map(int, c["xyxy"])
        cor = CORES.get(c["classe"], (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
        rotulo = f'{NOME_NA_TELA.get(c["classe"], c["classe"])} {c["conf"]:.2f}' + (f' #{c["id"]}' if c.get("id") is not None else "")
        escrever(frame, rotulo, (x1 + 4, max(18, y1 - 4)), cor, 0.5)
        # o "pé" da caixa (centro da borda de baixo) é onde a barreira toca o chão
        if na_zona(zona, (x1 + x2) / 2, y2) and (alerta is None or c["conf"] > alerta[1]):
            alerta = (c["classe"], c["conf"])

    camada = frame.copy()
    cv2.fillPoly(camada, [zona], VERMELHO if alerta else VERDE)
    cv2.addWeighted(camada, 0.22, frame, 0.78, 0, dst=frame)
    cv2.polylines(frame, [zona], True, VERMELHO if alerta else VERDE, 2)
    return alerta


def main() -> None:
    args = argumentos()
    from ultralytics import YOLO  # importado aqui para --help e testes rodarem sem ultralytics

    modelo = YOLO(args.modelo)
    fonte = int(args.fonte) if args.fonte.isdigit() else args.fonte
    cap = cv2.VideoCapture(fonte)
    if not cap.isOpened():
        raise SystemExit(f"Não consegui abrir a fonte de vídeo: {args.fonte}")
    ao_vivo = eh_ao_vivo(fonte)
    fps_fonte = cap.get(cv2.CAP_PROP_FPS) or 20.0
    leitor = LeitorAoVivo(cap) if ao_vivo else cap

    gravador = None
    pendentes: list[np.ndarray] = []   # ao vivo: primeiros quadros, até medir o FPS real
    fps_laco = deque(maxlen=30)
    ms_inferencia = deque(maxlen=30)
    todos_fps: list[float] = []
    ids_vistos: set[int] = set()
    contagem: Counter = Counter()
    quadros = 0

    while True:
        t0 = time.perf_counter()
        ok, frame = leitor.read()
        if not ok:
            break
        quadros += 1

        if args.rastrear:
            r = modelo.track(frame, conf=args.conf, imgsz=args.imgsz, persist=True, verbose=False)[0]
        else:
            r = modelo.predict(frame, conf=args.conf, imgsz=args.imgsz, verbose=False)[0]
        ms_inferencia.append(r.speed.get("inference", 0.0))

        ids = r.boxes.id.int().tolist() if (args.rastrear and r.boxes.id is not None) else [None] * len(r.boxes)
        caixas = [
            {"xyxy": xyxy, "classe": r.names[int(c)], "conf": float(cf), "id": i}
            for xyxy, c, cf, i in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist(), ids)
        ]
        for c in caixas:
            if c["id"] is not None and c["id"] not in ids_vistos:
                ids_vistos.add(c["id"])
                contagem[c["classe"]] += 1

        h, w = frame.shape[:2]
        alerta = desenhar(frame, caixas, zona_de_caminhada(w, h))

        dt = time.perf_counter() - t0
        fps_laco.append(1.0 / dt if dt > 0 else 0.0)
        todos_fps.append(fps_laco[-1])
        escrever(frame, f"FPS {np.mean(fps_laco):.1f} | inferencia {np.mean(ms_inferencia):.0f} ms", (10, 28))
        if args.rastrear and contagem:
            resumo = "  ".join(f"{NOME_NA_TELA.get(k, k)}: {v}" for k, v in sorted(contagem.items()))
            escrever(frame, f"barreiras no trajeto -> {resumo}", (10, 58), escala=0.5)
        if alerta:
            escrever(frame, f"ATENCAO: {NOME_NA_TELA.get(alerta[0], alerta[0])} a frente", (10, h - 20), VERMELHO, 0.9)

        if args.salvar:
            if gravador is None and not ao_vivo:
                gravador = abrir_gravador(args.salvar, fps_fonte, w, h)
            if gravador is not None:
                gravador.write(frame)
            else:
                # ao vivo, o modelo vê menos quadros do que a câmera produz: guarda os
                # primeiros até medir o FPS real e grava com ele, para tocar na velocidade certa
                pendentes.append(frame.copy())
                if len(pendentes) >= 30:
                    gravador = abrir_gravador(args.salvar, float(np.mean(todos_fps)), w, h)
                    for p in pendentes:
                        gravador.write(p)
                    pendentes.clear()

        if not args.sem_janela:
            cv2.imshow("Passo Firme - deteccao em tempo real", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break

    leitor.release()
    if pendentes and todos_fps:   # sessão ao vivo curta, com menos de 30 quadros
        h, w = pendentes[0].shape[:2]
        gravador = abrir_gravador(args.salvar, float(np.mean(todos_fps)), w, h)
        for p in pendentes:
            gravador.write(p)
    if gravador is not None:
        gravador.release()
    cv2.destroyAllWindows()

    print(f"\nQuadros processados: {quadros}")
    if todos_fps:
        print(f"FPS médio do laço completo (leitura + modelo + desenho): {np.mean(todos_fps):.1f}")
    if ao_vivo:
        print(f"Quadros da câmera descartados para não acumular atraso: {leitor.descartados}")
    if contagem:
        print("Barreiras distintas no trajeto:", dict(contagem))


if __name__ == "__main__":
    main()
