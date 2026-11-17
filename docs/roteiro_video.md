# Roteiro e transcrição do vídeo

**Vídeo de demonstração** (YouTube, não listado, 2 min 41 s): https://youtu.be/astTd2XMm9g

O vídeo mostra o detector funcionando de verdade: ao vivo em casa, pela câmera do celular, numa caminhada pelo Centro de Osasco e no serviço `/detectar`. O narrador aparece numa janela no canto. Cabeças e placas de quem não é do grupo foram pixeladas com `scripts/anonimizar_video.py`.

## Cenas

| Tempo | Cena | O que aparece |
| --- | --- | --- |
| 0:00 | Abertura | Título e uma calçada com buracos |
| 0:10 | O problema | 49.215 pedidos de conserto de calçada ao SP156 em 2025, com 33 dias de espera |
| 0:23 | Dados e treino | 180 fotos de São Paulo e 105 imagens abertas, 3 classes; diagrama do fluxo |
| 0:43 | Ao vivo | Câmera do celular pelo Wi-Fi: robô aspirador e lixeira marcados, zona vermelha, cerca de 12 FPS |
| 1:03 | Na calçada | Caminhada no Centro de Osasco: cones, cadeiras, sacos de lixo, vasos e postes |
| 1:28 | Serviço `/detectar` | Resposta em JSON e a foto com cabeça e placas pixeladas |
| 1:48 | Resultados | 0,30 de mAP50 em obstáculos, 81% das fotos com detecção, 12–14 FPS; exemplos de acerto |
| 2:08 | IA responsável | 0,89 × 0,11 (dataset aberto × ruas de São Paulo); tampa de bueiro tomada por buraco |
| 2:24 | Próximos passos | Novos exemplos a partir dos relatos revisados, mais bairros, rodar no celular |
| 2:34 | Fechamento | Integrantes e link do repositório |

## Transcrição da narração

**Abertura.** Andar a pé é o primeiro e o último trecho de qualquer deslocamento. Para um idoso ou uma pessoa com deficiência, um buraco ou um obstáculo na calçada pode significar uma queda.

**O problema.** Em São Paulo, os pedidos de conserto de calçada ao SP156 chegaram a 49 mil em 2025, com 33 dias de espera média. Falta saber onde estão as barreiras.

**Dados e treino.** O Passo Firme usa visão computacional para encontrá-las. Treinamos sob medida um detector YOLO26n, partindo dos pesos do COCO, com 180 fotos de calçadas de São Paulo tiradas a pé e 105 imagens de um dataset aberto. Anotamos três classes: buraco, desnível e obstáculo.

**Ao vivo.** Aqui ele roda ao vivo: o celular manda a câmera para o computador pelo Wi-Fi, e o modelo detecta a 12 quadros por segundo, só com o processador, sem placa de vídeo. Quando uma barreira entra na faixa à frente de quem anda, a zona fica vermelha e o aviso aparece. Cada barreira ganha um número e entra na contagem do trajeto.

**Na calçada.** Agora, uma calçada de verdade, no Centro de Osasco, uma cidade que o modelo nunca viu no treino. O mesmo modelo processou o vídeo quadro a quadro: cones, cadeiras, sacos de lixo, vasos e postes no caminho são marcados como obstáculos, e a zona fica vermelha quando eles entram na faixa à frente. Pessoas e placas aparecem pixeladas. A contagem do trajeto é o que vira o mapa de prioridades.

**Serviço `/detectar`.** O mesmo modelo também funciona como serviço: recebe uma foto e devolve cada barreira com tipo, posição e confiança, aqui três obstáculos, e pixela rostos e placas. É assim que a visão transforma o que vê em informação para o Passo Firme. Se o modelo não tiver certeza, uma pessoa revisa antes de encaminhar.

**Resultados.** No teste, com fotos de São Paulo que o modelo nunca viu, 81% das fotos com barreira recebem pelo menos uma detecção, e os obstáculos são o ponto forte, com mAP50 de 0,30. Dividir a foto em recortes fez o modelo achar cerca de 50% mais barreiras, e virou uma opção do serviço.

**IA responsável.** Usar fotos de São Paulo foi decisivo: um modelo igual acerta 0,89 em imagens do dataset aberto e só 0,11 nas nossas ruas. O que ainda precisa evoluir é buraco e desnível: na rua, uma tampa de bueiro foi confundida com buraco.

**Próximos passos.** O próximo passo é usar as fotos dos relatos, depois de revisadas, como novos exemplos de treino, de vários bairros.

**Fechamento.** Passo Firme: o olho que mapeia as barreiras da calçada.

## Como cada parte foi gravada

- **Ao vivo:** `python src/tempo_real.py --modelo modelos/best.pt --fonte http://IP-DO-CELULAR:4747/video --rastrear`, com a câmera do celular transmitida pelo app DroidCam e a tela do PC gravada.
- **Na calçada:** 3 minutos filmados com a câmera do celular e processados no PC com `--fonte caminhada.mp4 --rastrear --salvar`; os trechos usados passaram depois pelo `scripts/anonimizar_video.py`.
- **Serviço:** `uvicorn src.api:app --port 8001` e a página `/docs`, com a foto de teste `sp_se_1542016304509302.jpg`.
