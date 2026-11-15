# Serviço de visão do Passo Firme (POST /detectar), só CPU.
# Build:  docker build -t passo-firme-visao .
# Rodar:  docker run --rm -p 8001:8001 passo-firme-visao   ->  http://localhost:8001/docs
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    YOLO_CONFIG_DIR=/tmp/Ultralytics

# bibliotecas de sistema que o OpenCV usa
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-api.txt .
# PyTorch de CPU primeiro: a imagem fica bem menor que com a versão CUDA
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements-api.txt

COPY src/ src/
COPY modelos/best.pt modelos/best.pt

# usuário sem privilégios de root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# baixa no build o YOLO do COCO usado na anonimização, para o container não depender da internet ao subir
WORKDIR /app/modelos
RUN python -c "from ultralytics import YOLO; YOLO('yolo26n.pt')"
WORKDIR /app

ENV MODELO_PATH=modelos/best.pt \
    MODELO_COCO=modelos/yolo26n.pt

EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/saude', timeout=4)" || exit 1

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]
