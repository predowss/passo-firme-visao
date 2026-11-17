# Relatório (texto-base do PDF) — Applied Computer Vision

Estrutura exigida pela disciplina, na ordem: título, integrantes, resumo (250 palavras), introdução, objetivo (50 palavras), explicação técnica das ferramentas, metodologia passo a passo, exemplos de resultados e conclusão. As figuras estão em `resultados/`; o PDF final fica em `docs/relatorio.pdf`.

---

## Passo Firme: detecção de barreiras em calçadas com um YOLO26 treinado sob medida

**Global Solution 2026.2 · CitizenTech · Engenharia de Software, 4º ano (4ESPY)**
**Disciplina:** Applied Computer Vision · Profs. Arnaldo Viana e Paulo Rodrigues

**Integrantes**

| Nome | RM |
| --- | --- |
| David de Medeiros Pacheco Junior | RM551462 |
| Kaique Maia Reis Silva | RM552112 |
| Orlando Akio Morii Cardoso | RM98067 |
| Pedro Henrique Alves Guariente | RM550301 |

**Repositório:** https://github.com/predowss/passo-firme-visao · **Vídeo:** [link do YouTube, não listado — entra na edição de 18/11]

---

## Resumo

Calçadas com buracos, desníveis e obstáculos derrubam e isolam quem mais depende delas: idosos e pessoas com deficiência. Em São Paulo, os pedidos de conserto de calçada ao SP156 chegaram a 49.215 em 2025 e esperam, em média, 33 dias, sem um mapa que mostre onde estão as barreiras e quais são mais graves. Este trabalho apresenta o componente de visão computacional do Passo Firme, CitizenTech que mapeia, prioriza e encaminha barreiras de calçada. Treinamos de forma customizada um detector YOLO26n, a partir de pesos pré-treinados no COCO, para reconhecer três classes: buraco, desnível e obstáculo. O dataset combina 180 imagens de calçadas de São Paulo obtidas no Mapillary, capturadas a pé, anotadas com um guia único e divididas por sequência para evitar vazamento entre treino e teste, com 105 imagens de um dataset aberto de obstáculos, com as classes reagrupadas. No teste, só com ruas de São Paulo, o modelo atingiu mAP50 de 0,16 (0,30 em obstáculos), marcou ao menos uma barreira em 81% das fotos que tinham alguma e roda a 14,5 quadros por segundo num computador comum, sem placa de vídeo. Um modelo igual chega a 0,89 em imagens do dataset aberto que não viu: a diferença mostra quanto dados locais importam. O detector funciona em tempo real com a webcam ou a câmera do celular, avisa quando uma barreira entra na faixa à frente do pedestre e foi empacotado como serviço do aplicativo, que anonimiza rostos e placas e manda os casos incertos para revisão humana.

## Introdução

Andar a pé é o primeiro e o último trecho de qualquer deslocamento na cidade, e a calçada é onde ele acontece. Para um idoso, uma pessoa em cadeira de rodas ou alguém com deficiência visual, uma placa levantada ou um buraco não é incômodo: é queda, é desvio pela rua, é ficar em casa.

Os números de São Paulo mostram o tamanho do problema. Os pedidos ao SP156 sobre calçadas cresceram mais de 200% entre 2020 e 2025 e chegaram a 49.215, com espera média de 33 dias, sete vezes os 5 dias típicos do canal ([Câmara Municipal de SP, 2026](https://www.saopaulo.sp.leg.br/blog/subcomissao-de-calcadas-ouve-responsavel-pelo-servico-sp-156/)). Num estudo da USP com 1.434 adultos entrevistados por telefone, 88% disseram que as calçadas perto de casa não tinham estrutura adequada, com as zonas sul e leste em pior situação ([Portal Viva, 2026](https://viva.com.br/cidadania-e-direitos/estudo-da-usp-aponta-que-88-das-calcadas-de-sp-sao-irregulares.html)). Quatro em cada dez idosos em áreas urbanas têm medo de cair por defeitos nas calçadas ([Portal Viva, 2026](https://viva.com.br/saude-e-bem-estar/queda-em-idosos-nao-pode-ser-vista-como-normal-veja-cuidados-dentro-de-casa.html)), num país com 32,1 milhões de pessoas com 60 anos ou mais ([IBGE, Censo 2022](https://biblioteca.ibge.gov.br/visualizacao/livros/liv102038.pdf)).

O que falta não é reclamação, é informação organizada: onde estão as barreiras, de que tipo, e quais atrapalham mais gente. A visão computacional resolve a primeira parte: uma foto de celular, ou o vídeo de alguém caminhando, vira uma lista de barreiras com tipo, posição e confiança. Trabalhos recentes já usam a família YOLO para patologias de pavimento no Brasil, em geral na pista e vistas de um veículo (Monte et al., IME), e pesquisadores da USP publicaram o SideSeeing, um conjunto de vídeos e sensores para avaliar calçadas (Damaceno et al.). Aqui o ponto de vista é o do pedestre, e as classes foram escolhidas pelo risco para quem anda.

No Passo Firme, este componente é o "olho" do produto: o cidadão fotografa, o detector identifica a barreira, a IA generativa explica quem é o responsável pelo conserto e o robô de triagem encaminha.

## Objetivo

Treinar de forma customizada um detector de objetos YOLO26 que reconheça buracos, desníveis e obstáculos em calçadas de São Paulo em tempo real, sem deixar barreiras passarem despercebidas (alto recall), e entregá-lo como serviço do Passo Firme, que transforma fotos enviadas por cidadãos em barreiras mapeadas e priorizadas.

## Explicação técnica das ferramentas

**Detecção de objetos.** Um detector recebe uma imagem e devolve caixas delimitadoras, cada uma com uma classe e uma confiança. Diferente da classificação, que diz só "há um buraco nesta foto", a detecção diz onde está cada barreira, o que permite contar, localizar e alertar.

**YOLO26 (Ultralytics).** A família YOLO (*You Only Look Once*) detecta em uma única passada pela rede, o que a torna rápida o bastante para vídeo. A rede tem três partes: o *backbone* extrai características visuais (bordas, texturas, formas), o *neck* combina essas características em várias escalas, para achar tanto um buraco grande perto quanto um obstáculo pequeno ao fundo, e a *head* prevê as caixas e as classes. O YOLO26, anunciado em setembro de 2025 e lançado pela Ultralytics em janeiro de 2026 (biblioteca 8.4), foi desenhado para rodar em dispositivos de borda: dispensa a etapa de supressão de não máximos (NMS) na inferência e a *Distribution Focal Loss*, o que simplifica a implantação e acelera a CPU. Usamos a versão nano (YOLO26n, 2,4 milhões de parâmetros) como modelo principal e a small (YOLO26s, 9,5 milhões) para comparação.

**Transfer learning.** Em vez de treinar do zero, partimos dos pesos aprendidos no COCO (330 mil imagens, 80 classes do dia a dia). A rede já sabe reconhecer bordas, sombras e objetos; o ajuste fino ensina as nossas classes com centenas de imagens, e não milhões.

**Roboflow.** Plataforma usada para clonar datasets abertos do Roboflow Universe, reagrupar as classes deles nas nossas (ferramenta *Modify Classes*), anotar as imagens de São Paulo (com sugestões automáticas do *Label Assist*), dividir treino, validação e teste e exportar no formato YOLO.

**Mapillary.** Plataforma colaborativa de imagens de rua, com fotos publicadas sob licença CC BY-SA 4.0 e rostos e placas borrados automaticamente. Pela API, baixamos imagens de bairros escolhidos de São Paulo e, pela posição e pelo horário de cada foto, ficamos só com as sequências capturadas a pé, que têm o ponto de vista do pedestre.

**Google Colab.** Ambiente de notebooks com GPU NVIDIA T4 gratuita, usado para treinar e avaliar.

**OpenCV.** Biblioteca de visão usada para ler a câmera ou o vídeo, desenhar caixas, a zona de caminhada e os avisos, e pixelar as regiões sensíveis da imagem.

**Rastreamento.** O Ultralytics associa as caixas de um quadro ao seguinte com o rastreador BoT-SORT, o padrão da biblioteca. Cada barreira recebe um número que se mantém enquanto ela está à vista, o que permite contar as barreiras distintas de um trajeto.

**DroidCam.** Aplicativo que transforma o celular em câmera de rede: o PC lê o vídeo pelo Wi-Fi num endereço HTTP, como se fosse uma webcam.

**FastAPI e Docker.** O detector roda como um serviço HTTP (`POST /detectar`) empacotado num container, no formato que a API principal do Passo Firme espera (classe, confiança e caixa de cada barreira).

**Métricas.**
- *IoU (Intersection over Union):* sobreposição entre a caixa prevista e a anotada; acima de 0,5 conta como acerto.
- *Precisão:* das caixas que o modelo desenhou, a fração correta.
- *Recall:* das barreiras existentes, a fração encontrada. É a métrica mais importante para quem anda: um buraco não detectado custa mais que um falso alarme.
- *mAP50:* média, entre as classes, da área sob a curva precisão × recall com IoU ≥ 0,5. Não depende de um limiar de confiança.
- *mAP50-95:* a mesma média, exigindo caixas cada vez mais justas (IoU de 0,5 a 0,95).
- *Limiar de confiança:* precisão e recall dependem dele. O Ultralytics reporta os dois no limiar que maximiza o F1; por isso medimos também em limiares fixos. Limiar mais baixo encontra mais barreiras e traz mais falsos alarmes.

## Metodologia (passo a passo)

<!--FIGURA_FLUXO-->

1. **Definição das classes.** A anotação usou três classes escolhidas pelo risco para o pedestre: `buraco`, `desnivel` e `obstaculo`, com critérios no guia de anotação (`docs/guia_de_anotacao.md`). Também testamos juntar buraco e desnível numa classe só, `dano_no_piso` (ver passo 7).
2. **Dataset aberto.** Os datasets de calçada do Roboflow Universe que examinamos ou só anotam obstáculos, ou marcam a área da calçada em vez da barreira. Entrou um: o *Sidewalk obstacles* (Blindspot), do qual escolhemos a dedo 105 imagens com visão de pedestre, copiadas para o nosso projeto com *Clone Images*. O dataset tinha 24 classes, 15 delas com nomes numéricos (como `000000005669`) que eram rótulos trocados: abrindo as imagens, vimos que marcavam esferas de concreto, cones, balizadores, lixeiras e postes, mas também carros, pessoas, motos e bicicletas. As que marcam obstáculos foram reagrupadas em `obstaculo` (ferramenta *Modify Classes*) e as demais, descartadas; descartar todas às cegas teria deixado 193 obstáculos sem caixa. Essas imagens ficam só em treino e validação.

   | Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
   | --- | --- | --- | ---: | --- |
   | Sidewalk obstacles (Blindspot) | https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles | CC BY 4.0 | 105 | pole, warning_column, reflective_cone, spherical_roadblock, ashcan, fire_hydrant e 5 classes numéricas de obstáculos → obstaculo; pessoas, veículos e placas → descartados |

3. **Imagens de São Paulo (Mapillary).** 180 imagens de calçadas da região da Sé, no centro, baixadas com `scripts/baixar_mapillary.py`. O script calcula a velocidade de cada sequência pela posição e pelo horário das fotos e mantém só as capturadas a pé: velocidade mediana de 0,5 a 2,2 m/s, pico (percentil 90) de até 3,5 m/s e no máximo 30% dos trechos parados. Os dois últimos critérios foram acrescentados depois que um teste trouxe fotos de um carro no trânsito, cuja velocidade mediana parecia de pedestre. Ficam no máximo 8 imagens por sequência, com pelo menos 8 m entre elas, para evitar fotos quase iguais. Nos bairros da periferia testados (Itaquera e Jabaquara), nenhuma sequência passou no filtro: o acervo do Mapillary lá foi gravado quase todo de carro. Das 250 imagens baixadas, cada uma foi revisada e as que não mostravam calçada foram descartadas; ficaram 180, de 27 sequências. Todas são do mesmo colaborador do Mapillary e foram tiradas de dia, numa mesma data, o que é um viés que tratamos nas limitações. Autor e link de cada imagem estão em `dados/creditos_mapillary.csv` (licença CC BY-SA 4.0).
4. **Anotação.** Feita no Roboflow, com sugestões automáticas conferidas uma a uma, seguindo um guia único de caixas.
5. **Divisão sem vazamento.** Quatro sequências inteiras do Mapillary (31 imagens, 17% das fotos de SP) foram reservadas para o teste, para que a mesma barreira, fotografada por quem passou ali, nunca apareça no treino e no teste; as outras 23 sequências ficaram em treino e validação, sem nenhuma sequência nos dois lados. O teste tem só imagens de São Paulo. Divisão final da versão 1 do dataset (`v1-sp-blindspot`):

   | Conjunto | Imagens | Sem barreira | buraco | desnivel | obstaculo |
   | --- | ---: | ---: | ---: | ---: | ---: |
   | Treino (127 de SP + 89 abertas) | 216 | 21 | 58 | 52 | 463 |
   | Validação (22 de SP + 16 abertas) | 38 | 1 | 5 | 17 | 90 |
   | Teste (só SP) | 31 | 5 | 25 | 10 | 36 |

   O desequilíbrio é grande: há 463 obstáculos no treino e só 58 buracos e 52 desníveis.

6. **Treino.** Ajuste fino do YOLO26n no Colab (GPU T4), com os hiperparâmetros abaixo e o aumento de dados padrão do Ultralytics.

   | Parâmetro | Valor |
   | --- | --- |
   | Modelo base | yolo26n.pt (COCO) |
   | Imagem | 640 px (A e B) e 960 px (A2) |
   | Épocas | até 80, parada antecipada após 20 sem melhora; o A parou na época 66, com o melhor resultado na 46 |
   | Lote | 16 |
   | Semente | 42 |
   | Aumento de dados | mosaico, cor (HSV), escala, translação, espelhamento horizontal |

7. **Experimentos, em duas rodadas.**
   - *Rodada 1:* (A) YOLO26n em 640 px; (A2) o mesmo em 960 px, para ver se defeitos pequenos ficavam mais visíveis; (B) YOLO26s em 640 px. A resolução maior não ajudou (mAP50 de 0,15 contra 0,16 no teste) e deixou o modelo mais lento. A validação, que misturava imagens de SP e do dataset aberto, mostrou mAP50 de 0,94 nas abertas e de 0,20 nas de SP: a escolha do modelo estava sendo puxada pelo dataset aberto.
   - *Rodada 2:* a validação passou a ter só imagens de SP; as imagens abertas que estavam nela foram reservadas (16 imagens, fora do treino e da escolha) para medir a diferença. Comparamos (A) 3 classes, (C2) 2 classes, com `buraco` e `desnivel` juntos em `dano_no_piso`, e (B) YOLO26s com 3 classes. Até 100 épocas, parada após 30 sem melhora.
   - *Modelo final:* A da rodada 1 (YOLO26n, 3 classes, 640 px). No teste, os modelos das duas rodadas ficaram dentro da mesma margem para um conjunto de 31 imagens (mAP50 geral de 0,11 a 0,17; em obstáculo, 0,22 a 0,31), e juntar buraco e desnível não ajudou (0,03 em `dano_no_piso`). Por isso o critério de desempate foi o comportamento ao vivo: na câmera, o modelo A da rodada 1 detectou a mesma lixeira com confiança de 0,89 a 0,90, de forma estável, enquanto o C2 oscilava em torno de 0,26 e confundia a quina de uma estante com obstáculo.
8. **Avaliação.** Métricas no conjunto de teste (31 imagens de SP), por classe; matriz de confusão; precisão e recall em quatro limiares de confiança (0,10, 0,25, 0,35 e 0,50), com IoU de 0,5 e de 0,3, e por foto (`notebooks/03_limiar_confianca_colab.ipynb`); desempenho separado entre SP (teste) e dataset aberto (reserva); análise dos piores casos.
9. **Tempo real.** O modelo roda em `src/tempo_real.py` sobre a webcam, a câmera do celular (pelo app DroidCam, na mesma rede Wi-Fi) ou um vídeo gravado. Uma zona em forma de trapézio marca o chão logo à frente; se a base de uma caixa cai dentro dela, a zona fica vermelha e aparece o aviso. Com rastreamento, cada barreira recebe um ID e o trajeto termina com a contagem por tipo. Em fonte ao vivo, uma thread lê a câmera o tempo todo e o modelo recebe sempre o quadro mais recente: como a câmera produz mais quadros do que o modelo processa na CPU, os quadros velhos são descartados em vez de formar fila, e o atraso entre o mundo e a tela não cresce com o tempo. Antes de publicar um vídeo, `scripts/anonimizar_video.py` pixela cabeças e placas quadro a quadro.
10. **Serviço para o MVP.** O serviço `POST /detectar` recebe a foto do app, endireita a imagem pela orientação gravada no EXIF (fotos de celular costumam chegar deitadas), roda o detector na imagem original, pixela cabeças e placas (com um YOLO pré-treinado no COCO que acha pessoas e veículos, mais um detector de rostos) e devolve as detecções e a foto anonimizada, recodificada sem metadados (inclusive a localização do GPS); a foto original não é guardada nem registrada nos logs. Se nada for detectado ou a maior confiança ficar abaixo de 0,5, o relato vai para revisão humana antes de ser encaminhado. O serviço segue o contrato do MVP (classe, confiança e caixa, os campos da tabela `deteccao`) e tem Dockerfile; no MVP publicado no Azure, a rota ainda responde com dados simulados no mesmo formato, e ligar o detector real é publicar este container.

## Exemplos de resultados

**Desempenho geral no teste, modelo final (YOLO26n, 3 classes, rodada 1)**

| Métrica | Valor |
| --- | ---: |
| Precisão | 0,48 |
| Recall | 0,14 |
| mAP50 | 0,16 |
| mAP50-95 | 0,08 |
| Velocidade num PC de mesa sem placa de vídeo (AMD Ryzen 5 2600), `tempo_real.py` com a webcam | 14,5 FPS (57 ms por quadro) |
| Mesma máquina, câmera do celular pelo Wi-Fi | cerca de 12 FPS (inferência de 54 a 62 ms) |

**Por classe (teste):**

| Classe | Precisão | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| obstaculo | 0,57 | 0,28 | 0,30 | 0,17 |
| desnivel | 0,59 | 0,10 | 0,12 | 0,07 |
| buraco | 0,27 | 0,04 | 0,06 | 0,02 |

**O recall depende do limiar.** A tabela acima usa o limiar que maximiza o F1. Para ver a troca entre falsos alarmes e barreiras perdidas, medimos o modelo em limiares fixos, com dois critérios: IoU de 0,5 (a caixa precisa cobrir bem a anotada) e IoU de 0,3 (basta estar no lugar certo, que é o que importa para o pedestre e para o app).

| Confiança mínima | Precisão (IoU 0,5) | Recall (IoU 0,5) | Precisão (IoU 0,3) | Recall (IoU 0,3) | Recall de obstáculo (IoU 0,3) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0,10 | 0,24 | 0,25 | 0,34 | 0,35 | 0,56 |
| 0,25 (serviço) | 0,35 | 0,21 | 0,42 | 0,25 | 0,39 |
| 0,35 (tempo real) | 0,43 | 0,17 | 0,54 | 0,21 | 0,33 |
| 0,50 | 0,65 | 0,15 | 0,71 | 0,17 | 0,31 |

Contando por foto, que é como o cidadão usa o app, o quadro é outro:

| Confiança mínima | Fotos com barreira que receberam ao menos uma detecção (de 26) | Fotos sem barreira com alarme falso (de 5) |
| ---: | ---: | ---: |
| 0,10 | 25 (96%) | 3 |
| 0,25 (serviço) | 21 (81%) | 2 |
| 0,35 (tempo real) | 16 (62%) | 2 |
| 0,50 | 11 (42%) | 1 |

Com o limiar de 0,25 do serviço, 4 em cada 5 fotos com barreira chegam com pelo menos uma barreira marcada, mesmo que o modelo não encontre todas as barreiras da foto (recall por caixa de 0,21 a 0,25). As fotos em que nada é detectado não se perdem: vão para revisão humana. É por isso que o serviço usa um limiar baixo e uma pessoa no circuito, em vez de um limiar alto, que daria menos falsos alarmes e deixaria mais da metade das fotos com barreira sem nenhuma marcação.

**Rodada 1, efeito da resolução (teste):** YOLO26n 640: mAP50 0,16, 11 FPS na CPU do Colab; YOLO26n 960: mAP50 0,15, 7 FPS. Aumentar a imagem não fez buraco e desnível aparecerem.

**Rodada 2, comparação de modelos (teste):**

| Modelo | Precisão | Recall | mAP50 | ms por imagem (GPU T4) |
| --- | ---: | ---: | ---: | ---: |
| YOLO26n, 3 classes (A) | 0,15 | 0,20 | 0,11 | 8,2 |
| YOLO26n, 2 classes (C2) | 0,27 | 0,21 | 0,17 | 4,1 |
| YOLO26s, 3 classes (B) | 0,40 | 0,16 | 0,17 | 5,6 |

O modelo small não superou o nano: com tão poucas imagens, o tamanho do modelo não é o gargalo.

**Velocidade na CPU:** 90 ms por imagem na CPU do Colab (11 FPS) e 14,5 FPS no PC do grupo com a webcam (AMD Ryzen 5 2600, sem placa de vídeo).

**SP × dataset aberto (IA responsável):**

| Grupo | Imagens | Precisão | Recall | mAP50 |
| --- | ---: | ---: | ---: | ---: |
| São Paulo (teste) | 31 | 0,15 | 0,20 | 0,11 |
| Dataset aberto (reserva, nunca visto) | 16 | 0,94 | 0,83 | 0,89 |

(Modelo de 3 classes da rodada 2: nessa rodada, as 16 imagens abertas ficaram fora do treino e da escolha da época.) O mesmo modelo acerta muito mais nas imagens do dataset aberto, de outro país, com objetos grandes e fundo limpo, do que nas calçadas de São Paulo, com lixo, pisos variados e sombras. Um detector treinado só com dados prontos pareceria ótimo e falharia justamente onde vai ser usado.

**Teste em ambiente real (16/11).** Com a câmera do celular transmitindo para o PC pelo Wi-Fi, o detector rodou a cerca de 12 FPS e marcou uma lixeira com confiança de 0,85 a 0,87, mantendo o mesmo ID de rastreio enquanto ela estava à frente, e um robô aspirador no chão com até 0,88, acionando a zona de alerta. Também mostrou os limites: um cachorro deitado e uma árvore no caminho não geraram alerta, porque não são tipos de barreira que o modelo aprendeu, e a quina de uma porta gerou um falso alarme.

**Figuras** (cada uma com legenda no PDF):
- Figura 1: fluxo do componente, dos dados ao uso do modelo (`resultados/fluxo.png`), no início da metodologia.
- Figura 2: curvas de perda e métricas por época no treino do modelo A (`resultados/A_yolo26n/results.png`).
- Figura 3: matriz de confusão normalizada no teste; a maior parte dos erros é barreira não encontrada, e não troca entre classes (`resultados/A_teste/confusion_matrix_normalized.png`).
- Figura 4: exemplos de acerto no teste; verde é a anotação e vermelho a previsão (`resultados/exemplos_acerto.png`).
- Figura 5: os seis piores casos do teste (`resultados/piores_casos.png`).
- Figura 6: tempo real com a zona de alerta acionada, pela webcam (lixeira 0,89, 14,3 FPS na tela) e pela câmera do celular (lixeira 0,87, 11 FPS na tela no momento da captura) (`resultados/tempo_real_modeloA.jpeg` e `resultados/tempo_real_celular.jpg`).
- Figura 7: resposta do `/detectar` desenhada na foto: três obstáculos (0,90, 0,77 e 0,70), uma cabeça e três placas pixeladas (`resultados/detectar_resposta_caixas.jpg`).

**Análise de erros.** Os erros dos seis piores casos (Figura 5) caem em cinco padrões:

| # | O que o modelo fez | Causa provável | Correção proposta |
| --- | --- | --- | --- |
| 1 | Não viu barreiras pequenas a mais de uns 10 m (painéis 1 e 3) nem um saco de lixo preto no meio da calçada, na divisa entre sol e sombra forte (painel 1) | A 640 px, um objeto distante ocupa poucos pixels; o contraste forte de luz esconde objetos escuros | Anotar só até a distância útil ao pedestre, recortar a imagem em blocos na inferência e incluir mais fotos com sombra dura |
| 2 | Marcou "buraco" (0,50 e 0,40) com uma caixa grande sobre a área de pedras soltas, enquanto a anotação tinha caixas pequenas dentro dela (painéis 1 e 2) | Dano no piso não tem borda clara: a caixa no lugar certo fica com IoU abaixo de 0,5 e conta como um falso alarme e um erro ao mesmo tempo | Regra única no guia (uma caixa por área contínua) e avaliar também com IoU menor ou com segmentação |
| 3 | Marcou como obstáculo (0,37 e 0,41) um copo e um papel no chão que não estavam anotados (painéis 1 e 2) | O guia não fixava um tamanho mínimo para lixo miúdo, que ora foi anotado, ora não | Definir o que conta como barreira (o que atrapalha a passagem) e revisar as anotações com essa regra |
| 4 | Não viu blocos de isopor e de concreto ao lado de um caminhão (painel 5) | Tipos de obstáculo que quase não aparecem no treino | Mais fotos de SP com obstáculos variados |
| 5 | Não viu lixo miúdo sobre o piso ondulado de pedra portuguesa (painel 3) | A textura forte do piso, típica do centro, esconde objetos pequenos | Mais fotos com pedra portuguesa |

## Conclusão

O objetivo foi atingido em parte. O grupo treinou de forma customizada um YOLO26n para barreiras de calçada que roda em tempo real num computador comum, sem placa de vídeo (14,5 FPS com a webcam e cerca de 12 FPS com a câmera do celular), avisa quando uma barreira entra na faixa à frente do pedestre e foi empacotado como serviço, com anonimização e revisão humana. Obstáculos são reconhecidos de forma estável: mAP50 de 0,30 no teste e detecções firmes ao vivo, como a lixeira com 0,87 a 0,90. No uso do app, com o limiar de 0,25, 81% das fotos de teste com barreira chegam com pelo menos uma barreira marcada, e as demais vão para revisão humana.

Buraco (mAP50 de 0,06) e desnível (0,12) não foram aprendidos. São formas irregulares, sem borda clara, com cerca de 110 exemplos no treino contra 463 obstáculos, e juntar as duas classes não ajudou. Parte do erro vem da própria medida: caixas no lugar certo, mas de tamanho diferente da anotação, contam como erro com IoU de 0,5. Por caixa, o recall fica entre 0,14 e 0,35 conforme o limiar e a exigência de sobreposição, longe do alto recall que o objetivo pedia; por foto, chega a 81% com o limiar do serviço. Por isso o sistema usa limiar baixo e uma pessoa confirma os casos incertos, em vez de deixar barreiras passarem sem ninguém ver.

A maior lição é sobre dados. Um modelo igual chega a 0,89 em imagens do dataset aberto e a 0,11 nas ruas de São Paulo, e a primeira rodada mostrou que uma validação misturada escolhia o modelo pelo dataset errado. Um detector para calçadas brasileiras precisa de fotos brasileiras, de vários bairros, colaboradores, horários e climas.

**Limitações e como o sistema lida com elas.**

| Limitação | O que o sistema já faz | Próximo passo |
| --- | --- | --- |
| **Buraco e desnível pouco aprendidos** (mAP50 de 0,06 e 0,12, com cerca de 110 exemplos no treino; juntar as duas classes não ajudou) | Limiar baixo (0,25) e revisão humana: foto sem detecção ou com confiança abaixo de 0,5 não é encaminhada sem uma pessoa ver. Assim, 81% das fotos de teste com barreira já chegam com ao menos uma marcação, e as outras não se perdem | Usar as fotos confirmadas pelos cidadãos no app como novos rótulos, priorizando dano no piso, com as regras de anotação revistas (guia, seção 7) |
| **Fotos de uma só região** (Sé), de um único colaborador do Mapillary, tiradas de dia, numa mesma data | Divisão por sequência e teste só com ruas de SP, para não superestimar o desempenho; o que não foi medido (periferia, chuva, noite) está declarado | Coletar em outros bairros, com chuva e à noite, e medir por região com o `scripts/avaliar_por_regiao.py`, que já está pronto |
| **Teste pequeno** (31 fotos, 71 barreiras) | Diferenças de poucos centésimos entre modelos não são tratadas como ganho; o desempate do modelo final foi o comportamento ao vivo | Ampliar o teste com sequências novas, que não entram no treino |
| **Só reconhece o tipo de barreira que aprendeu** (no teste ao vivo, um cachorro deitado e uma árvore no caminho não geraram alerta) | O escopo está declarado (três classes), e no app a foto sem detecção vai para revisão humana | Acrescentar classes, como veículo na calçada, ou testar um detector de vocabulário aberto, como o YOLOE-26 da Ultralytics |
| **Anonimização por heurística** | Duas camadas (pessoas e veículos do COCO e detector de rosto), sobre fotos que o Mapillary já borra; a foto original não é guardada | Revisão humana das fotos antes de aparecerem no mapa público |

**Outros próximos passos.** Estimar o tamanho da barreira para priorizar o conserto, rodar o modelo no próprio celular, sem internet, e usar a câmera do robô vistoriador do Maker Lab.

## Referências

- Câmara Municipal de São Paulo. Subcomissão de Calçadas ouve responsável pelo serviço SP 156. 13/08/2026. https://www.saopaulo.sp.leg.br/blog/subcomissao-de-calcadas-ouve-responsavel-pelo-servico-sp-156/
- Portal Viva. Estudo da USP aponta que 88% das calçadas de SP são irregulares. 16/07/2026. https://viva.com.br/cidadania-e-direitos/estudo-da-usp-aponta-que-88-das-calcadas-de-sp-sao-irregulares.html
- Portal Viva. Queda em idosos não pode ser vista como normal. 24/06/2026. https://viva.com.br/saude-e-bem-estar/queda-em-idosos-nao-pode-ser-vista-como-normal-veja-cuidados-dentro-de-casa.html
- IBGE. Censo Demográfico 2022. https://biblioteca.ibge.gov.br/visualizacao/livros/liv102038.pdf
- Ultralytics. YOLO26 — documentação dos modelos. https://docs.ultralytics.com/models/
- Ultralytics. Ultralytics Launches YOLO26 (Business Wire, 14/01/2026). https://www.businesswire.com/news/home/20260114168538/en
- Monte, D. M. F. M. do; Goldschmidt, R. R.; Santos, M. dos. Identificação e Classificação de Patologias em Pavimentos Rodoviários Flexíveis e Rígidos Utilizando YOLOv8. WebMedia, SBC. https://sol.sbc.org.br/index.php/webmedia/article/download/37973/37751
- Damaceno, R. J. P. et al. SideSeeing: a multimodal dataset and collection of tools for sidewalk assessment. arXiv:2407.06464. https://arxiv.org/abs/2407.06464
- Mapillary. CC BY-SA license for open data. https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- Mapillary. Image privacy. https://help.mapillary.com/hc/en-us/articles/115001770349
- Roboflow. Preprocess Images (Modify Classes). https://docs.roboflow.com/datasets/dataset-versions/image-preprocessing
- Blindspot. Sidewalk obstacles Dataset. Roboflow Universe, 2023. https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles
