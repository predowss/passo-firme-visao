"""Pixela cabeças e placas de um vídeo inteiro, quadro a quadro, antes de publicar.

O tempo real (`src/tempo_real.py`) mostra a câmera sem anonimizar, para não perder FPS.
Este script passa depois sobre o vídeo gravado (o `--salvar` do tempo real ou o vídeo
filmado pelo celular) e esconde cabeças de pessoas e placas de veículos com a mesma
função usada pela API (`src/anonimizar.py`).

Uso (da raiz do repositório):
  py scripts/anonimizar_video.py resultados/demo.mp4 resultados/demo_anonimo.mp4

Opções:
  --modelo-coco  YOLO do COCO que acha pessoas e veículos (padrão: yolo26n.pt)
  --com-haar     também usa as cascatas Haar de rosto (desligado: no vídeo elas
                 piscam em pontos aleatórios; o YOLO já cobre as cabeças)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import src.anonimizar as anon  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Anonimiza um vídeo quadro a quadro.")
    p.add_argument("entrada", help="vídeo de entrada (.mp4)")
    p.add_argument("saida", help="vídeo anonimizado (.mp4)")
    p.add_argument("--modelo-coco", default="yolo26n.pt")
    p.add_argument("--com-haar", action="store_true")
    a = p.parse_args()

    if not a.com_haar:
        anon._CASCATAS_ROSTO = []

    from ultralytics import YOLO

    cap = cv2.VideoCapture(a.entrada)
    if not cap.isOpened():
        raise SystemExit(f"Não consegui abrir {a.entrada}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    gravador = cv2.VideoWriter(a.saida, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    modelo = YOLO(a.modelo_coco)

    n, cabecas, placas = 0, 0, 0
    inicio = time.perf_counter()
    while True:
        ok, quadro = cap.read()
        if not ok:
            break
        quadro, resumo = anon.anonimizar(quadro, modelo)
        cabecas += resumo.get("cabecas", 0)
        placas += resumo.get("placas", 0)
        gravador.write(quadro)
        n += 1
        if n % 60 == 0:
            print(f"{n}/{total} quadros ({time.perf_counter() - inicio:.0f} s)")
    cap.release()
    gravador.release()
    print(f"Pronto: {n} quadros em {a.saida} | regiões pixeladas: {cabecas} cabeças, {placas} placas")


if __name__ == "__main__":
    main()
