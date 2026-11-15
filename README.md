# Passo Firme — Visão Computacional

Detector de barreiras em calçadas (buraco, desnível e obstáculo) treinado sob medida com YOLO26, rodando em tempo real e integrado ao app do Passo Firme.

**Global Solution 2026.2 · CitizenTech · Engenharia de Software, 4º ano · Applied Computer Vision**

- **Vídeo de demonstração:** [link do YouTube, não listado]
- **Relatório (PDF):** [`docs/relatorio.pdf`](docs/relatorio.pdf)
- **Notebook de treino com as saídas:** [`notebooks/01_treino_yolo26_colab.ipynb`](notebooks/01_treino_yolo26_colab.ipynb)
- **Dataset no Roboflow:** [link público]

## Integrantes

| Nome | RM |
| --- | --- |
| David de Medeiros Pacheco Junior | RM551462 |
| Kaique Maia Reis Silva | RM552112 |
| Orlando Akio Morii Cardoso | RM98067 |
| Pedro Henrique Alves Guariente | RM550301 |

## Ficha Técnica do MVP

| Campo | Conteúdo |
| --- | --- |
| Nome do produto | Passo Firme |
| Cidadão e território | Idosos, pessoas com deficiência e pedestres que dependem de andar a pé, num distrito piloto de São Paulo |
| Problema, em uma frase | Buracos, degraus e obstáculos nas calçadas derrubam e isolam justamente quem mais depende delas, e ninguém tem a visão do todo para priorizar o conserto |
| Proposta de valor | Para o cidadão, de graça: fotografou, a IA identifica a barreira, explica quem é o responsável pela lei e encaminha. Para quem conserta: mapa priorizado por risco e população afetada, com prova em foto |
| Arquitetura: componentes | App web acessível · API FastAPI + PostgreSQL · **detector YOLO (este repositório)** · assistente da lei (LLM local + RAG) · pipeline Airflow → Databricks · robô de triagem (RPA) · robô vistoriador (Maker Lab) · containers no Azure com Terraform e GitHub Actions |
| Modelos de IA utilizados | **YOLO26n treinado para barreiras de calçada** · LLM aberto pequeno com RAG e LoRA · embeddings multilíngues · TinyML no robô |
| URL do MVP e repositório | [URL do MVP] · [link deste repositório] |
| ODS conectados | 11 (metas 11.2 e 11.7) · 10 (meta 10.2) · 3 · 9 (meta 9.1) |

## O papel da visão no Passo Firme

O cidadão fotografa a calçada no app. A API principal manda a foto para `POST /detectar`, que devolve as barreiras (classe, confiança e caixa) e a foto com cabeças e placas pixeladas. Se o modelo não tiver certeza (confiança abaixo de 0,5), o relato vai para revisão humana antes de ser encaminhado.

## Resultados

Conjunto de teste com fotos de ruas que o modelo nunca viu.

| Métrica (YOLO26n) | Valor |
| --- | ---: |
| mAP50 | [X] |
| mAP50-95 | [X] |
| Precisão | [X] |
| Recall | [X] |
| Velocidade na CPU de um notebook | [X] FPS |

[Figura: `resultados/exemplos_acerto.png`]

Detalhes por classe, comparação nano × small, periferia × centro e análise de erros estão no relatório e no notebook.

## Como reproduzir

### 1. Dataset

Siga `docs/guia_de_anotacao.md` (classes, fotos, anonimização e divisão por rua). O dataset final está no Roboflow; o notebook baixa a versão usada.

### 2. Treino (Google Colab, GPU T4)

Abra `notebooks/01_treino_yolo26_colab.ipynb` no Colab, crie o segredo `ROBOFLOW_API_KEY`, preencha workspace, projeto e versão, e rode as células em ordem. Ao fim, baixe o `best.pt` para `modelos/`.

### 3. Tempo real (no seu computador)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# webcam
python src/tempo_real.py --modelo modelos/best.pt --fonte 0
# câmera do celular (app de transmissão na mesma rede Wi-Fi)
python src/tempo_real.py --modelo modelos/best.pt --fonte http://IP-DO-CELULAR:8080/video --rastrear
# vídeo gravado, salvando o resultado
python src/tempo_real.py --modelo modelos/best.pt --fonte caminhada.mp4 --salvar resultados/demo.mp4
```

### 4. Serviço `/detectar`

```bash
pip install -r requirements-api.txt
uvicorn src.api:app --port 8001        # documentação em http://localhost:8001/docs

# ou com Docker
docker build -t passo-firme-visao .
docker run --rm -p 8001:8001 passo-firme-visao
```

Exemplo de chamada:

```bash
curl -F "foto=@calcada.jpg" "http://localhost:8001/detectar?devolver_imagem=false"
```

```json
{
  "id": "6f1c…",
  "largura": 1280, "altura": 720,
  "deteccoes": [
    {"classe": "buraco", "confianca": 0.87, "caixa": [512.3, 401.8, 690.0, 560.2]}
  ],
  "total": 1,
  "revisao_humana": false,
  "anonimizacao": {"cabecas": 1, "placas": 0, "rostos": 0, "metodos": ["yolo_coco"]},
  "modelo": "best.pt",
  "tempo_ms": 142.7
}
```

### 5. Avaliação por região (opcional, fora do Colab)

```bash
python scripts/contar_classes.py dados/<dataset>/data.yaml
python scripts/avaliar_por_regiao.py --modelo modelos/best.pt --dados dados/<dataset>/data.yaml \
    --grupo periferia=sp_itaquera,sp_jabaquara --grupo centro=sp_paulista
```

## Estrutura

```
├── notebooks/01_treino_yolo26_colab.ipynb   treino, avaliação e figuras (com saídas)
├── src/
│   ├── tempo_real.py      detecção ao vivo com zona de alerta, FPS e contagem
│   ├── api.py             serviço POST /detectar (FastAPI)
│   └── anonimizar.py      pixela cabeças e placas (LGPD)
├── scripts/
│   ├── contar_classes.py      tabela do dataset por classe e conjunto
│   └── avaliar_por_regiao.py  métricas por grupo de imagens (periferia × centro)
├── docs/
│   ├── guia_de_anotacao.md    regras de coleta, anotação e divisão
│   ├── relatorio_rascunho.md  texto-base do PDF
│   └── roteiro_video.md       roteiro e checklist do vídeo
├── dados/      README com links e licenças dos datasets
├── modelos/    best.pt treinado
├── resultados/ figuras e tabelas
├── Dockerfile
├── requirements.txt / requirements-api.txt
```

## Dados, licenças e privacidade

- Datasets abertos do Roboflow Universe, cada um com autor, link e licença em `dados/README.md`.
- Fotos próprias tiradas pelo grupo em vias públicas, com rostos e placas pixelados antes do upload.
- O serviço não guarda a foto original nem registra localização ou nome de arquivo nos logs.

## Limitações

[Preencher depois da avaliação: ex.: menos exemplos noturnos e de chuva; anonimização por heurística.]
