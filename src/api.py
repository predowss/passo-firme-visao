"""Serviço de visão do Passo Firme: recebe uma foto de calçada e devolve as barreiras.

A API principal do MVP (POST /relatos) chama este serviço. Ordem do que acontece:
  1. valida o arquivo (tamanho e se é imagem de verdade);
  2. roda o detector treinado na imagem original;
  3. anonimiza a imagem (cabeças e placas) e só essa cópia sai daqui;
  4. marca revisão humana quando o modelo não tem certeza.

Rodar localmente (da raiz do repositório):
  uvicorn src.api:app --host 0.0.0.0 --port 8001
  # documentação interativa em http://localhost:8001/docs

Variáveis de ambiente (todas opcionais):
  MODELO_PATH       pesos treinados                     (padrão: modelos/best.pt)
  MODELO_COCO       YOLO do COCO para anonimizar; ""=off (padrão: yolo26n.pt)
  CONF_MIN          confiança mínima de uma detecção     (padrão: 0.25)
  LIMIAR_REVISAO    abaixo disto, vai para revisão humana (padrão: 0.50)
  MAX_MB            tamanho máximo da foto em MB         (padrão: 8)
"""
from __future__ import annotations

import base64
import logging
import os
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from ultralytics import YOLO

from src.anonimizar import anonimizar

MODELO_PATH = os.getenv("MODELO_PATH", "modelos/best.pt")
MODELO_COCO = os.getenv("MODELO_COCO", "yolo26n.pt")
CONF_MIN = float(os.getenv("CONF_MIN", "0.25"))
LIMIAR_REVISAO = float(os.getenv("LIMIAR_REVISAO", "0.50"))
MAX_BYTES = int(float(os.getenv("MAX_MB", "8")) * 1024 * 1024)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("passo-firme-visao")

if not Path(MODELO_PATH).exists():
    raise RuntimeError(f"Modelo não encontrado em {MODELO_PATH}. Copie o best.pt do Colab para modelos/.")

detector = YOLO(MODELO_PATH)
modelo_coco = YOLO(MODELO_COCO) if MODELO_COCO else None

app = FastAPI(
    title="Passo Firme - Visão",
    description="Detecta barreiras em fotos de calçada (dano no piso e obstáculo, ou buraco, desnível e obstáculo, conforme o modelo) e devolve a foto anonimizada.",
    version="1.0.0",
)


@app.get("/saude")
def saude() -> dict:
    return {
        "status": "ok",
        "modelo": Path(MODELO_PATH).name,
        "classes": list(detector.names.values()),
        "anonimizacao": bool(modelo_coco),
    }


@app.post("/detectar")
async def detectar(
    foto: UploadFile = File(..., description="Foto da calçada (JPG ou PNG)"),
    devolver_imagem: bool = Query(True, description="Devolver a foto anonimizada em base64"),
) -> dict:
    dados = await foto.read()
    if len(dados) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"Foto maior que {MAX_BYTES // (1024 * 1024)} MB.")
    img = cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=422, detail="O arquivo enviado não é uma imagem válida.")

    inicio = time.perf_counter()
    r = detector.predict(img, conf=CONF_MIN, imgsz=640, verbose=False)[0]
    deteccoes = [
        {
            "classe": r.names[int(c)],
            "confianca": round(float(cf), 3),
            "caixa": [round(float(v), 1) for v in xyxy],  # x1, y1, x2, y2 em pixels da foto enviada
        }
        for xyxy, c, cf in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist())
    ]
    deteccoes.sort(key=lambda d: d["confianca"], reverse=True)

    limpa, resumo_anon = anonimizar(img, modelo_coco)
    tempo_ms = (time.perf_counter() - inicio) * 1000

    maior = deteccoes[0]["confianca"] if deteccoes else 0.0
    resposta = {
        "id": str(uuid.uuid4()),
        "largura": img.shape[1],
        "altura": img.shape[0],
        "deteccoes": deteccoes,
        "total": len(deteccoes),
        # nada detectado ou detecção incerta: uma pessoa confirma antes de encaminhar
        "revisao_humana": maior < LIMIAR_REVISAO,
        "anonimizacao": resumo_anon,
        "modelo": Path(MODELO_PATH).name,
        "tempo_ms": round(tempo_ms, 1),
    }
    if devolver_imagem:
        ok, jpg = cv2.imencode(".jpg", limpa, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ok:
            resposta["imagem_anonimizada_jpg_base64"] = base64.b64encode(jpg.tobytes()).decode("ascii")

    # log sem foto, sem nome de arquivo e sem localização: só o necessário para monitorar
    log.info(
        "detectar id=%s total=%d maior_conf=%.2f revisao=%s tempo_ms=%.0f",
        resposta["id"], resposta["total"], maior, resposta["revisao_humana"], tempo_ms,
    )
    return resposta
