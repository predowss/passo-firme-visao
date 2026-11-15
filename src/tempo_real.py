"""Detecção de barreiras de calçada em tempo real (webcam, celular ou vídeo).

Desenha as caixas, mede o FPS e marca no chão uma "zona de caminhada" (o trecho
logo à frente de quem anda). Quando uma barreira entra nessa zona, a zona fica
vermelha e aparece o aviso na tela, como um alerta em realidade aumentada.

Exemplos:
  # webcam do notebook
  python src/tempo_real.py --modelo modelos/best.pt --fonte 0

  # câmera do celular pelo app IP Webcam (Android), na mesma rede Wi-Fi
  python src/tempo_real.py --modelo modelos/best.pt --fonte http://192.168.0.10:8080/video

  # vídeo gravado andando na calçada, salvando o resultado para o vídeo de entrega
  python src/tempo_real.py --modelo modelos/best.pt --fonte caminhada.mp4 --salvar resultados/demo.mp4

  # contando barreiras distintas ao longo do trajeto (rastreamento com IDs)
  python src/tempo_real.py --modelo modelos/best.pt --fonte caminhada.mp4 --rastrear

Teclas: q ou Esc para sair.
"""
from __future__ import annotations

import argparse
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
}
VERDE = (80, 175, 76)
VERMELHO = (36, 28, 237)


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
        rotulo = f'{c["classe"]} {c["conf"]:.2f}' + (f' #{c["id"]}' if c.get("id") is not None else "")
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

    gravador = None
    fps_laco = deque(maxlen=30)
    ms_inferencia = deque(maxlen=30)
    todos_fps: list[float] = []
    ids_vistos: set[int] = set()
    contagem: Counter = Counter()
    quadros = 0

    while True:
        t0 = time.perf_counter()
        ok, frame = cap.read()
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
            resumo = "  ".join(f"{k}: {v}" for k, v in sorted(contagem.items()))
            escrever(frame, f"barreiras no trajeto -> {resumo}", (10, 58), escala=0.5)
        if alerta:
            escrever(frame, f"ATENCAO: {alerta[0]} a frente", (10, h - 20), VERMELHO, 0.9)

        if args.salvar:
            if gravador is None:
                fps_video = cap.get(cv2.CAP_PROP_FPS) or 20.0
                gravador = cv2.VideoWriter(args.salvar, cv2.VideoWriter_fourcc(*"mp4v"), fps_video, (w, h))
            gravador.write(frame)

        if not args.sem_janela:
            cv2.imshow("Passo Firme - deteccao em tempo real", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break

    cap.release()
    if gravador is not None:
        gravador.release()
    cv2.destroyAllWindows()

    print(f"\nQuadros processados: {quadros}")
    if todos_fps:
        print(f"FPS médio do laço completo (leitura + modelo + desenho): {np.mean(todos_fps):.1f}")
    if contagem:
        print("Barreiras distintas no trajeto:", dict(contagem))


if __name__ == "__main__":
    main()
