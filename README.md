# Passo Firme — Visão Computacional

Detector de barreiras em calçadas (buraco, desnível e obstáculo) treinado sob medida com YOLO26, rodando em tempo real na CPU e empacotado como o serviço `POST /detectar` do Passo Firme.

**Global Solution 2026.2 · CitizenTech · Engenharia de Software, 4º ano (4ESPY) · Applied Computer Vision**

- **Vídeo de demonstração:** em edição; o link do YouTube (não listado) entra aqui até 19/11
- **Relatório (PDF):** [`docs/relatorio.pdf`](docs/relatorio.pdf) (texto-base em [`docs/relatorio_rascunho.md`](docs/relatorio_rascunho.md))
- **Notebooks com as saídas:** [treino, rodada 1](notebooks/01_treino_yolo26_colab.ipynb) · [treino, rodada 2](notebooks/02_treino_rodada2_colab.ipynb) · [precisão e recall por limiar](notebooks/03_limiar_confianca_colab.ipynb)
- **Dataset no Roboflow:** https://universe.roboflow.com/pedros-workspace-md4aw/passo-firme-calcadas (versão 1, `v1-sp-blindspot`)

![Detecção ao vivo pela câmera do celular: a lixeira é marcada como obstáculo e a zona de caminhada fica vermelha](resultados/tempo_real_ao_vivo.gif)

*Detecção ao vivo, com a câmera do celular transmitida pelo Wi-Fi para um PC sem placa de vídeo (16/11/2026).*

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
| Fontes de dados | SP156 (dados abertos da Prefeitura) · Open-Meteo (chuva) · API do IBGE (população) · relatos do app (foto + GPS) · leituras do robô · **imagens de calçadas de São Paulo do Mapillary e o dataset aberto *Sidewalk obstacles* (este repositório)** · Lei 15.442/2011, Decreto 59.671/2020, Lei 13.146/2015 e Carta de Serviços do SP156 |
| Modelos de IA utilizados | **YOLO26n treinado para barreiras de calçada (este repositório)** · YOLO26n do COCO para anonimizar pessoas e placas · LLM aberto pequeno com RAG e LoRA · embeddings multilíngues · TinyML no robô |
| URL do MVP e repositório | MVP: https://ca-passofirme-api.lemonfield-b3da2f2c.brazilsouth.azurecontainerapps.io/docs · repositório principal: https://github.com/predowss/passo-firme · este repositório: https://github.com/predowss/passo-firme-visao |
| Indicadores de impacto | Barreiras mapeadas · % resolvidas · tempo médio até o conserto (antes, pelo histórico do SP156, e depois) · idosos e pessoas com deficiência usando o app · metros de calçada vistoriados pelo robô |
| ODS conectados | 11 (metas 11.2 e 11.7) · 10 (meta 10.2) · 3 · 9 (meta 9.1) |

## O papel da visão no Passo Firme

O cidadão fotografa a calçada no app. A API principal manda a foto para `POST /detectar`, que devolve as barreiras (classe, confiança e caixa, os mesmos campos da tabela `deteccao` do banco do MVP) e a foto com cabeças e placas pixeladas. Se nada for detectado ou a maior confiança ficar abaixo de 0,5, o relato vai para revisão humana antes de ser encaminhado. Fotos de celular são endireitadas pela orientação gravada no EXIF antes da detecção, e a foto devolvida sai sem metadados (inclusive o GPS).

**Situação da integração:** este repositório entrega o serviço pronto, com Dockerfile. No MVP publicado no Azure, a rota `/detectar` ainda devolve uma resposta simulada no mesmo formato; ligar o detector real é publicar este container e apontar a API principal para ele.

O mesmo modelo roda em tempo real (`src/tempo_real.py`) sobre a webcam, a câmera do celular ou um vídeo gravado: uma zona em trapézio marca o chão à frente do pedestre e fica vermelha quando uma barreira entra nela.

![Fluxo do componente de visão: dados e treino, e uso do modelo no tempo real e no serviço /detectar](resultados/fluxo.png)

## Resultados

Modelo final: YOLO26n, 3 classes, 640 px. Conjunto de teste com 31 fotos de calçadas de São Paulo, de sequências que o modelo nunca viu.

| Métrica (teste, 31 imagens de SP) | Valor |
| --- | ---: |
| mAP50 | 0,16 |
| mAP50-95 | 0,08 |
| Precisão | 0,48 |
| Recall | 0,14 |
| Velocidade num PC de mesa sem placa de vídeo (AMD Ryzen 5 2600) | 14,5 FPS com a webcam · cerca de 12 FPS com a câmera do celular pelo Wi-Fi |

| Classe | Precisão | Recall | mAP50 |
| --- | ---: | ---: | ---: |
| obstaculo | 0,57 | 0,28 | 0,30 |
| desnivel | 0,59 | 0,10 | 0,12 |
| buraco | 0,27 | 0,04 | 0,06 |

Precisão e recall da tabela são medidos no limiar de confiança que maximiza o F1. Em limiares fixos (`notebooks/03_limiar_confianca_colab.ipynb`, tabela completa em `resultados/limiares.csv`):

| Confiança mínima | Precisão | Recall | Fotos com barreira com ao menos uma detecção | Fotos sem barreira com alarme falso |
| ---: | ---: | ---: | ---: | ---: |
| 0,10 | 0,24 | 0,25 | 25 de 26 (96%) | 3 de 5 |
| 0,25 (serviço) | 0,35 | 0,21 | 21 de 26 (81%) | 2 de 5 |
| 0,35 (tempo real) | 0,43 | 0,17 | 16 de 26 (62%) | 2 de 5 |
| 0,50 | 0,65 | 0,15 | 11 de 26 (42%) | 1 de 5 |

Precisão e recall por caixa com IoU de 0,5. Com o limiar de 0,25 do serviço, 4 em cada 5 fotos com barreira chegam com pelo menos uma barreira marcada; as fotos sem nenhuma detecção vão para revisão humana, em vez de se perderem.

**Dados locais fazem diferença:** um modelo igual acerta mAP50 de 0,89 em 16 imagens do dataset aberto que não viu e só 0,11 nas ruas de São Paulo.

![Exemplos de acerto no teste](resultados/exemplos_acerto.png)

Detalhes por rodada, comparação nano × small, resolução 640 × 960, 3 × 2 classes e análise dos piores casos estão no relatório e nos notebooks.

## Como reproduzir

Os comandos usam `python`; no Windows, use `py`. Testado com Python 3.14 no Windows (PC do grupo, AMD Ryzen 5 2600, sem placa de vídeo) e com Python 3.13 e Ultralytics 8.4.214 no Colab.

### 1. Dataset

As imagens de São Paulo vêm do Mapillary, filtradas para sequências capturadas a pé e separadas por bairro:

```bash
set "MAPILLARY_TOKEN=MLY|..."          # Windows (cmd); no Linux/Mac: export MAPILLARY_TOKEN='MLY|...'
python scripts/baixar_mapillary.py --regiao se
```

Quando o bairro só tem sequências gravadas de carro, `--listar` mostra as mais lentas e `--sequencia "bairro=CHAVE"` baixa as escolhidas a dedo (detalhes no guia de anotação). Completam o dataset 105 imagens do dataset aberto *Sidewalk obstacles* (Blindspot), clonadas no Roboflow com as classes reagrupadas em `obstaculo`.

Depois, siga `docs/guia_de_anotacao.md` (classes, revisão das imagens, anotação e divisão por sequência). O dataset final está no Roboflow; os notebooks baixam a versão usada.

### 2. Treino (Google Colab, GPU T4)

Abra `notebooks/01_treino_yolo26_colab.ipynb` no Colab, crie o segredo `ROBOFLOW_API_KEY` (painel de chave à esquerda, com acesso liberado para o notebook), confira workspace, projeto e versão e use *Executar tudo*. Ao fim, o notebook baixa o `best.pt`; coloque-o em `modelos/`. O `notebooks/02_treino_rodada2_colab.ipynb` repete o treino com a validação só de São Paulo e a variante de 2 classes.

### 3. Tempo real (no seu computador)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# webcam
python src/tempo_real.py --modelo modelos/best.pt --fonte 0 --rastrear
# câmera do celular pelo Wi-Fi (ex.: app DroidCam, mesma rede)
python src/tempo_real.py --modelo modelos/best.pt --fonte http://IP-DO-CELULAR:4747/video --rastrear
# vídeo gravado, salvando o resultado anotado
python src/tempo_real.py --modelo modelos/best.pt --fonte caminhada.mp4 --rastrear --salvar resultados/demo.mp4
```

Tecla `q` encerra; o script imprime o FPS médio e a contagem de barreiras do trajeto. Em câmera ao vivo, uma thread lê a câmera o tempo todo e o modelo sempre recebe o quadro mais recente, então o atraso não cresce mesmo quando o modelo é mais lento que a câmera; com `--salvar`, o vídeo ao vivo é gravado com o FPS medido, para tocar na velocidade real. Antes de publicar um vídeo, pixele cabeças e placas:

```bash
python scripts/anonimizar_video.py resultados/demo.mp4 resultados/demo_anonimo.mp4
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

Resposta real para a foto `sp_se_1542016304509302.jpg` do teste (saco de lixo, cone e monte de lixo na calçada):

```json
{
  "id": "a426609b-a27e-4024-a2e7-fc70d5e6ead5",
  "largura": 1920, "altura": 1080,
  "deteccoes": [
    {"classe": "obstaculo", "confianca": 0.897, "caixa": [554, 596.4, 907.5, 821.1]},
    {"classe": "obstaculo", "confianca": 0.771, "caixa": [359.6, 97.7, 441.1, 253.8]},
    {"classe": "obstaculo", "confianca": 0.699, "caixa": [879.3, 203.4, 999.2, 275.2]}
  ],
  "total": 3,
  "revisao_humana": false,
  "anonimizacao": {"cabecas": 1, "placas": 3, "rostos": 0, "metodos": ["yolo_coco", "haar_rosto"]},
  "modelo": "best.pt",
  "tempo_ms": 2064
}
```

A primeira chamada leva cerca de 2 s porque carrega os modelos; as seguintes são mais rápidas. Com `devolver_imagem=true`, a resposta traz também a foto anonimizada em base64.

![Resposta do /detectar desenhada na foto: três obstáculos, cabeça e placas pixeladas](resultados/detectar_resposta_caixas.jpg)

### 5. Avaliação por grupo de imagens (opcional, fora do Colab)

```bash
python scripts/contar_classes.py dados/<dataset>/data.yaml
python scripts/avaliar_por_regiao.py --modelo modelos/best.pt --dados dados/<dataset>/data.yaml \
    --grupo centro=sp_se,sp_paulista --grupo periferia=sp_periferia
```

## Estrutura

```
├── notebooks/
│   ├── 01_treino_yolo26_colab.ipynb   rodada 1: treino, avaliação e figuras (com saídas)
│   ├── 02_treino_rodada2_colab.ipynb  rodada 2: validação só de SP, 2 classes (com saídas)
│   └── 03_limiar_confianca_colab.ipynb precisão e recall por limiar e por foto (com saídas)
├── src/
│   ├── tempo_real.py      detecção ao vivo com zona de alerta, FPS e contagem
│   ├── api.py             serviço POST /detectar (FastAPI)
│   └── anonimizar.py      pixela cabeças e placas (LGPD)
├── scripts/
│   ├── baixar_mapillary.py    imagens de SP por bairro, só sequências a pé, com créditos
│   ├── contar_classes.py      tabela do dataset por classe e conjunto
│   ├── avaliar_por_regiao.py  métricas por grupo de imagens (bairros, SP × aberto)
│   └── anonimizar_video.py    pixela cabeças e placas de um vídeo inteiro antes de publicar
├── docs/
│   ├── relatorio_rascunho.md  texto-base do PDF
│   ├── guia_de_anotacao.md    regras de coleta, anotação e divisão
│   └── roteiro_video.md       roteiro e checklist do vídeo
├── dados/      README com links, licenças e créditos dos datasets
├── modelos/    best.pt treinado
├── resultados/ figuras do relatório, GIF do tempo real e tabela de limiares
├── Dockerfile
└── requirements.txt / requirements-api.txt
```

## Dados, licenças e privacidade

- Dataset aberto *Sidewalk obstacles* (Blindspot), do Roboflow Universe, CC BY 4.0, com link e mapeamento das classes em `dados/README.md`.
- Imagens de calçadas de São Paulo do [Mapillary](https://www.mapillary.com), licença CC BY-SA 4.0, capturadas a pé e já com rostos e placas borrados pela plataforma. Autor e link de cada imagem em `dados/creditos_mapillary.csv`.
- O dataset é uma coleção: as anotações e a documentação do grupo estão sob CC BY 4.0; as imagens do Mapillary entram sem alteração e continuam sob CC BY-SA 4.0, com os créditos acima.
- O código usa a biblioteca Ultralytics, distribuída sob AGPL-3.0; o serviço e o modelo `best.pt`, treinado com ela, seguem essa licença.
- O serviço não guarda a foto original nem registra localização ou nome de arquivo nos logs; só a cópia anonimizada sai dele, sem os metadados EXIF.

## Limitações e como o sistema lida com elas

| Limitação | O que o sistema já faz | Próximo passo |
| --- | --- | --- |
| **Buraco e desnível pouco aprendidos** (mAP50 de 0,06 e 0,12, com cerca de 110 exemplos no treino; juntar as duas classes não ajudou) | Limiar baixo (0,25) e revisão humana: foto sem detecção ou com confiança abaixo de 0,5 não é encaminhada sem uma pessoa ver. Assim, 81% das fotos de teste com barreira já chegam com ao menos uma marcação, e as outras não se perdem | Usar as fotos confirmadas pelos cidadãos no app como novos rótulos, priorizando dano no piso, com as regras de anotação revistas (guia, seção 7) |
| **Fotos de uma só região** (Sé), de um único colaborador do Mapillary, tiradas de dia, numa mesma data | Divisão por sequência e teste só com ruas de SP, para não superestimar o desempenho; o que não foi medido (periferia, chuva, noite) está declarado | Coletar em outros bairros, com chuva e à noite, e medir por região com o `scripts/avaliar_por_regiao.py`, que já está pronto |
| **Teste pequeno** (31 fotos, 71 barreiras) | Diferenças de poucos centésimos entre modelos não são tratadas como ganho; o desempate do modelo final foi o comportamento ao vivo | Ampliar o teste com sequências novas, que não entram no treino |
| **Só reconhece o tipo de barreira que aprendeu** (no teste ao vivo, um cachorro deitado e uma árvore no caminho não geraram alerta) | O escopo está declarado (três classes), e no app a foto sem detecção vai para revisão humana | Acrescentar classes, como veículo na calçada, ou testar um detector de vocabulário aberto, como o YOLOE-26 da Ultralytics |
| **Anonimização por heurística** | Duas camadas (pessoas e veículos do COCO e detector de rosto), sobre fotos que o Mapillary já borra; a foto original não é guardada | Revisão humana das fotos antes de aparecerem no mapa público |
