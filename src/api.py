"""Serviço de visão do Passo Firme: recebe uma foto de calçada e devolve as barreiras.

Implementa o POST /detectar do contrato do MVP: a API principal (POST /relatos) chama
este serviço quando ele está publicado. No MVP do Azure, a rota ainda devolve uma
resposta simulada no mesmo formato. Ordem do que acontece:
  1. valida o arquivo (tamanho e se é imagem de verdade);
  2. endireita a foto pela orientação EXIF e roda o detector treinado na imagem original;
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
import io
import logging
import os
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from PIL import Image, ImageOps
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
    description="Detecta barreiras em fotos de calçada (buraco, desnível e obstáculo) com um YOLO26n treinado pelo grupo e devolve a foto com cabeças e placas pixeladas. Sem detecção ou com confiança abaixo de 0,5, o relato vai para revisão humana.",
    version="1.0.0",
)


def ler_foto(dados: bytes) -> np.ndarray | None:
    """Abre a foto enviada já na orientação certa.

    Fotos de celular costumam vir deitadas, com a rotação só anotada no EXIF; aplicamos
    essa rotação antes de detectar. Os metadados (inclusive GPS) ficam para trás: a
    imagem segue como pixels e a cópia devolvida é recodificada sem EXIF.
    """
    try:
        with Image.open(io.BytesIO(dados)) as foto:
            foto = ImageOps.exif_transpose(foto).convert("RGB")
            return cv2.cvtColor(np.asarray(foto), cv2.COLOR_RGB2BGR)
    except Exception:
        return None


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
    img = ler_foto(dados)
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
