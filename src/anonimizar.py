"""Anonimização de fotos do Passo Firme (LGPD by design).

Borra (pixela) cabeças de pessoas e a região da placa de veículos antes de a foto
ser guardada ou devolvida pela API. A detecção de barreiras roda na imagem
original; só a cópia anonimizada sai do serviço.

Como funciona:
  1. Um YOLO pré-treinado no COCO (yolo26n.pt) acha pessoas e veículos.
     - pessoa  -> pixela o topo da caixa (cabeça), de frente, de costas ou de lado;
     - veículo -> pixela a faixa de baixo da caixa, onde ficam as placas.
  2. Se o OpenCV instalado trouxer as cascatas Haar de rosto, elas reforçam a
     busca por rostos que o YOLO não pegou (ex.: rosto muito perto da câmera).

Uso pela linha de comando (uma foto ou uma pasta inteira):
  python src/anonimizar.py foto.jpg foto_anonima.jpg
  python src/anonimizar.py fotos_brutas/ fotos_anonimas/
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

PESSOA = 0                 # índices das classes no COCO
VEICULOS = {2, 3, 5, 7}    # carro, moto, ônibus, caminhão
FRACAO_CABECA = 0.22       # parte de cima da caixa da pessoa que é pixelada
FRACAO_PLACA = 0.45        # parte de baixo da caixa do veículo que é pixelada
BLOCOS = 6                 # a região vira uma grade de ~6 blocos na largura


def _carregar_cascatas() -> list:
    """Carrega as cascatas Haar de rosto, se existirem nesta instalação do OpenCV."""
    pasta = getattr(getattr(cv2, "data", None), "haarcascades", None)
    if not pasta:
        return []
    cascatas = []
    for nome in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        caminho = Path(pasta) / nome
        if caminho.exists():
            c = cv2.CascadeClassifier(str(caminho))
            if not c.empty():
                cascatas.append(c)
    return cascatas


_CASCATAS_ROSTO = _carregar_cascatas()


def pixelar(img: np.ndarray, x1: float, y1: float, x2: float, y2: float) -> bool:
    """Pixela a região (x1, y1, x2, y2) da imagem, no lugar. Devolve False se a região for vazia."""
    h, w = img.shape[:2]
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(round(x2))), min(h, int(round(y2)))
    if x2 - x1 < 2 or y2 - y1 < 2:
        return False
    roi = img[y1:y2, x1:x2]
    rw, rh = roi.shape[1], roi.shape[0]
    pequeno_w = max(1, min(BLOCOS, rw))
    pequeno_h = max(1, min(rh, round(BLOCOS * rh / rw)))
    pequeno = cv2.resize(roi, (pequeno_w, pequeno_h), interpolation=cv2.INTER_AREA)
    img[y1:y2, x1:x2] = cv2.resize(pequeno, (rw, rh), interpolation=cv2.INTER_NEAREST)
    return True


def regioes_sensiveis(img: np.ndarray, modelo_coco=None, conf: float = 0.35) -> dict:
    """Devolve as caixas a esconder: {'cabecas': [...], 'placas': [...], 'rostos': [...]}."""
    regioes = {"cabecas": [], "placas": [], "rostos": []}

    if modelo_coco is not None:
        r = modelo_coco.predict(img, conf=conf, classes=[PESSOA, *VEICULOS], verbose=False)[0]
        for (x1, y1, x2, y2), c in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist()):
            altura = y2 - y1
            if int(c) == PESSOA:
                regioes["cabecas"].append((x1, y1, x2, y1 + FRACAO_CABECA * altura))
            else:
                regioes["placas"].append((x1, y2 - FRACAO_PLACA * altura, x2, y2))

    if _CASCATAS_ROSTO:
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        for cascata in _CASCATAS_ROSTO:
            achados = cascata.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=6, minSize=(24, 24))
            for (x, y, w, h) in achados:
                # margem de 15% para cobrir cabelo e orelhas
                mx, my = 0.15 * w, 0.15 * h
                regioes["rostos"].append((x - mx, y - my, x + w + mx, y + h + my))

    return regioes


def anonimizar(img: np.ndarray, modelo_coco=None, conf: float = 0.35) -> tuple[np.ndarray, dict]:
    """Devolve (cópia anonimizada, resumo com quantas regiões foram escondidas por tipo)."""
    saida = img.copy()
    regioes = regioes_sensiveis(saida, modelo_coco, conf)
    resumo = {}
    for tipo, caixas in regioes.items():
        resumo[tipo] = sum(pixelar(saida, *caixa) for caixa in caixas)
    resumo["metodos"] = (["yolo_coco"] if modelo_coco is not None else []) + (
        ["haar_rosto"] if _CASCATAS_ROSTO else []
    )
    return saida, resumo


def _main(argv: list[str]) -> None:
    if len(argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    from ultralytics import YOLO  # importado aqui para o módulo funcionar sem ultralytics nos testes

    entrada, saida = Path(argv[1]), Path(argv[2])
    modelo = YOLO("yolo26n.pt")
    if entrada.is_dir():
        saida.mkdir(parents=True, exist_ok=True)
        arquivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        pares = [(p, saida / p.name) for p in arquivos]
    else:
        pares = [(entrada, saida)]
    for origem, destino in pares:
        img = cv2.imread(str(origem))
        if img is None:
            print(f"pulei (não é imagem): {origem}")
            continue
        limpa, resumo = anonimizar(img, modelo)
        cv2.imwrite(str(destino), limpa)
        print(f"{origem.name}: {resumo}")


if __name__ == "__main__":
    _main(sys.argv)
