# Rascunho do relatório (PDF) — Applied Computer Vision

Estrutura exigida pela disciplina, na ordem: título, integrantes, resumo (250 palavras), introdução, objetivo (50 palavras), explicação técnica das ferramentas, metodologia passo a passo, exemplos de resultados e conclusão.

Trechos entre colchetes, como `[X]`, saem do notebook depois do treino. Ao terminar, colem num editor de texto, ponham as figuras e exportem em PDF.

---

## Passo Firme: detecção de barreiras em calçadas com um YOLO26 treinado sob medida

**Global Solution 2026.2 · CitizenTech · Engenharia de Software, 4º ano (4ESPY)**
**Disciplina:** Applied Computer Vision · Profs. Arnaldo Viana e Paulo Rodrigues

**Integrantes**

| Nome | RM |
| --- | --- |
| David de Medeiros Pacheco Junior | RM551462 |
| Kaique Maia Reis Silva | RM552112 |
| Orlando Akio Morii Cardoso | RM98067 (conferir: tem 5 dígitos) |
| Pedro Henrique Alves Guariente | RM550301 |

**Repositório:** [link do GitHub] · **Vídeo:** [link do YouTube, não listado]

---

## Resumo

Calçadas com buracos, desníveis e obstáculos derrubam e isolam justamente quem mais depende delas: idosos e pessoas com deficiência. Em São Paulo, os pedidos de conserto de calçada ao SP156 chegaram a 49.215 em 2025 e esperam, em média, 33 dias, sem um mapa que mostre onde estão as barreiras e quais são mais graves. Este trabalho apresenta o componente de visão computacional do Passo Firme, uma CitizenTech que mapeia, prioriza e encaminha barreiras de calçada. Treinamos de forma customizada um detector YOLO26n, a partir de pesos pré-treinados no COCO, para reconhecer três classes: buraco, desnível e obstáculo. O conjunto de dados combina 180 imagens de calçadas de São Paulo obtidas no Mapillary, capturadas a pé, anotadas segundo um guia único e divididas por sequência para evitar vazamento entre treino e teste, com 105 imagens de um dataset aberto de obstáculos de calçada, com as classes reagrupadas para o nosso problema. No teste, só com ruas de São Paulo, o modelo atingiu mAP50 de 0,16 (0,30 em obstáculos), rodando a 14,5 quadros por segundo na CPU de um notebook. Na mesma configuração, o detector chega a 0,89 em imagens do dataset aberto que não viu: a diferença mostra quanto dados locais importam. O detector funciona em tempo real com a webcam ou a câmera do celular, avisa quando uma barreira entra na faixa à frente do pedestre e está publicado como serviço do aplicativo, que anonimiza rostos e placas e envia casos de baixa confiança para revisão humana.

*(248 palavras; depois de preencher, confiram se continua perto de 250.)*

## Introdução

Andar a pé é o primeiro e o último trecho de qualquer deslocamento na cidade, e a calçada é onde ele acontece. Para um idoso, uma pessoa em cadeira de rodas ou alguém com deficiência visual, uma placa levantada ou um buraco não é incômodo: é queda, é desvio pela rua, é ficar em casa.

Os números de São Paulo mostram o tamanho do problema. Os pedidos ao SP156 sobre calçadas cresceram mais de 200% entre 2020 e 2025 e chegaram a 49.215, com espera média de 33 dias, sete vezes os 5 dias típicos do canal ([Câmara Municipal de SP, 2026](https://www.saopaulo.sp.leg.br/blog/subcomissao-de-calcadas-ouve-responsavel-pelo-servico-sp-156/)). Num estudo da USP com 1.434 adultos entrevistados por telefone, 88% disseram que as calçadas perto de casa não tinham estrutura adequada, com as zonas sul e leste em pior situação ([Portal Viva, 2026](https://viva.com.br/cidadania-e-direitos/estudo-da-usp-aponta-que-88-das-calcadas-de-sp-sao-irregulares.html)). Quatro em cada dez idosos em áreas urbanas têm medo de cair por defeitos nas calçadas ([Portal Viva, 2026](https://viva.com.br/saude-e-bem-estar/queda-em-idosos-nao-pode-ser-vista-como-normal-veja-cuidados-dentro-de-casa.html)), num país com 32,1 milhões de pessoas com 60 anos ou mais ([IBGE, Censo 2022](https://biblioteca.ibge.gov.br/visualizacao/livros/liv102038.pdf)).

O que falta não é reclamação, é informação organizada: onde estão as barreiras, de que tipo, e quais atrapalham mais gente. A visão computacional resolve a primeira parte: uma foto de celular, ou o vídeo de alguém caminhando, vira uma lista de barreiras com tipo, posição e confiança. Trabalhos recentes já usam a família YOLO para patologias de pavimento no Brasil, em geral na pista e vistas de um veículo (Monte et al., IME), e pesquisadores da USP publicaram o SideSeeing, um conjunto de vídeos e sensores para avaliar calçadas (Damaceno et al.). Aqui o ponto de vista é o do pedestre, e as classes foram escolhidas pelo risco para quem anda.

No Passo Firme, este componente é o "olho" do produto: o cidadão fotografa, o detector identifica a barreira, a IA generativa explica quem é o responsável pelo conserto e o robô de triagem encaminha.

## Objetivo

Treinar de forma customizada um detector de objetos YOLO26 que reconheça buracos, desníveis e obstáculos em calçadas de São Paulo em tempo real, sem deixar barreiras passarem despercebidas (alto recall), e integrá-lo ao Passo Firme para transformar fotos enviadas por cidadãos em barreiras mapeadas e priorizadas.

*(46 palavras.)*

## Explicação técnica das ferramentas

**Detecção de objetos.** Um detector recebe uma imagem e devolve caixas delimitadoras, cada uma com uma classe e uma confiança. Diferente da classificação, que diz só "há um buraco nesta foto", a detecção diz onde está cada barreira, o que permite contar, localizar e alertar.

**YOLO26 (Ultralytics).** A família YOLO (*You Only Look Once*) detecta em uma única passada pela rede, o que a torna rápida o bastante para vídeo. A rede tem três partes: o *backbone* extrai características visuais (bordas, texturas, formas), o *neck* combina essas características em várias escalas, para achar tanto um buraco grande perto quanto um obstáculo pequeno ao fundo, e a *head* prevê as caixas e as classes. O YOLO26, lançado pela Ultralytics em janeiro de 2026, foi desenhado para rodar em dispositivos de borda e dispensa a etapa de supressão de não máximos (NMS) na inferência, o que simplifica a implantação. Usamos a versão nano (YOLO26n) como modelo principal e a small (YOLO26s) para comparação.

**Transfer learning.** Em vez de treinar do zero, partimos dos pesos aprendidos no COCO (330 mil imagens, 80 classes do dia a dia). A rede já sabe reconhecer bordas, sombras e objetos; o ajuste fino ensina as nossas classes com centenas de imagens, e não milhões.

**Roboflow.** Plataforma usada para clonar datasets abertos do Roboflow Universe, reagrupar as classes deles nas nossas (ferramenta *Modify Classes*), anotar as imagens de São Paulo (com sugestões automáticas do *Label Assist*), dividir treino, validação e teste e exportar no formato YOLO.

**Mapillary.** Plataforma colaborativa de imagens de rua, com fotos publicadas sob licença CC BY-SA 4.0 e rostos e placas borrados automaticamente. Pela API, baixamos imagens de bairros escolhidos de São Paulo e, pela posição e pelo horário de cada foto, ficamos só com as sequências capturadas a pé, que têm o ponto de vista do pedestre.

**Google Colab.** Ambiente de notebooks com GPU NVIDIA T4 gratuita, usado para treinar e avaliar.

**OpenCV.** Biblioteca de visão usada para ler a câmera ou o vídeo, desenhar caixas, a zona de caminhada e os avisos, e pixelar as regiões sensíveis da imagem.

**FastAPI e Docker.** O detector roda como um serviço HTTP (`POST /detectar`) empacotado num container, chamado pela API principal do Passo Firme.

**Métricas.**
- *IoU (Intersection over Union):* sobreposição entre a caixa prevista e a anotada; acima de 0,5 conta como acerto.
- *Precisão:* das caixas que o modelo desenhou, a fração correta.
- *Recall:* das barreiras existentes, a fração encontrada. É a métrica mais importante para quem anda: um buraco não detectado custa mais que um falso alarme.
- *mAP50:* média, entre as classes, da área sob a curva precisão × recall com IoU ≥ 0,5.
- *mAP50-95:* a mesma média, exigindo caixas cada vez mais justas (IoU de 0,5 a 0,95).

## Metodologia (passo a passo)

1. **Definição das classes.** A anotação usou três classes escolhidas pelo risco para o pedestre: `buraco`, `desnivel` e `obstaculo`, com critérios no guia de anotação (`docs/guia_de_anotacao.md`). Também testamos juntar buraco e desnível numa classe só, `dano_no_piso` (ver passo 7).
2. **Dataset aberto.** Os datasets de calçada do Roboflow Universe que examinamos ou só anotam obstáculos, ou marcam a área da calçada em vez da barreira. Entrou um: o *Sidewalk obstacles* (Blindspot), do qual escolhemos a dedo 105 imagens com visão de pedestre, copiadas para o nosso projeto com *Clone Images*. O dataset tinha 24 classes, 15 delas com nomes numéricos (como `000000005669`) que eram rótulos trocados: abrindo as imagens, vimos que marcavam esferas de concreto, cones, balizadores, lixeiras e postes, mas também carros, pessoas, motos e bicicletas. As que marcam obstáculos foram reagrupadas em `obstaculo` (ferramenta *Modify Classes*) e as demais, descartadas; descartar todas às cegas teria deixado 193 obstáculos sem caixa. Essas imagens ficam só em treino e validação.

   | Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
   | --- | --- | --- | ---: | --- |
   | Sidewalk obstacles (Blindspot) | https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles | CC BY 4.0 | 105 | pole, warning_column, reflective_cone, spherical_roadblock, ashcan, fire_hydrant e 5 classes numéricas de obstáculos → obstaculo; pessoas, veículos e placas → descartados |

3. **Imagens de São Paulo (Mapillary).** [N] imagens de calçadas de [bairros, ex.: região da Sé], baixadas com `scripts/baixar_mapillary.py`. O script calcula a velocidade de cada sequência pela posição e pelo horário das fotos e mantém só as capturadas a pé: velocidade mediana de 0,5 a 2,2 m/s, pico (percentil 90) de até 3,5 m/s e no máximo 30% dos trechos parados. Os dois últimos critérios foram acrescentados depois que um teste trouxe fotos de um carro no trânsito, cuja velocidade mediana parecia de pedestre. Ficam no máximo 8 imagens por sequência, com pelo menos 8 m entre elas, para evitar fotos quase iguais. Nos bairros da periferia testados (Itaquera e Jabaquara), nenhuma sequência passou no filtro: o acervo do Mapillary lá foi gravado quase todo de carro. Nesses casos, o script lista as sequências mais lentas para escolha manual. Cada imagem foi revisada; as que não mostravam calçada foram descartadas, e ficaram 149 para treino e validação e 31 para teste. Autor e link de cada uma estão em `dados/creditos_mapillary.csv` (licença CC BY-SA 4.0).
4. **Anotação.** Feita no Roboflow, com sugestões automáticas conferidas uma a uma, seguindo um guia único de caixas.
5. **Divisão sem vazamento.** Sequências inteiras do Mapillary reservadas para o teste ([N] sequências, cerca de 15% das imagens), para que a mesma barreira, fotografada por quem passou ali, nunca apareça no treino e no teste. O teste tem só imagens de São Paulo. Divisão final: [N] treino, [N] validação, [N] teste.

   [Tabela do dataset por classe e conjunto: saída `tabela_dataset` do notebook]

6. **Treino.** Ajuste fino do YOLO26n no Colab (GPU T4), com os hiperparâmetros abaixo e o aumento de dados padrão do Ultralytics.

   | Parâmetro | Valor |
   | --- | --- |
   | Modelo base | yolo26n.pt (COCO) |
   | Imagem | 640 (A) e 960 (A2); B na resolução escolhida |
   | Épocas | até 80, parada antecipada após 20 sem melhora (parou na [N]) |
   | Lote | 16 |
   | Aumento de dados | mosaico, cor (HSV), escala, translação, espelhamento horizontal |

7. **Experimentos, em duas rodadas.**
   - *Rodada 1:* (A) YOLO26n em 640 px; (A2) o mesmo em 960 px, para ver se defeitos pequenos ficavam mais visíveis; (B) YOLO26s em 640 px. A resolução maior não ajudou (mAP50 de 0,15 contra 0,16 no teste) e deixou o modelo mais lento. A validação, que misturava imagens de SP e do dataset aberto, mostrou mAP50 de 0,94 nas abertas e de 0,20 nas de SP: a escolha do modelo estava sendo puxada pelo dataset aberto.
   - *Rodada 2:* a validação passou a ter só imagens de SP; as imagens abertas que estavam nela foram reservadas (16 imagens, fora do treino e da escolha) para medir a diferença. Comparamos (A) 3 classes, (C2) 2 classes, com `buraco` e `desnivel` juntos em `dano_no_piso`, e (B) YOLO26s com 3 classes. Até 100 épocas, parada após 30 sem melhora.
   - *Modelo final:* A da rodada 1 (YOLO26n, 3 classes, 640 px). No teste, os modelos das duas rodadas ficaram dentro da mesma margem para um conjunto de 31 imagens (mAP50 geral de 0,11 a 0,17; em obstáculo, 0,22 a 0,31), e juntar buraco e desnível não ajudou (0,03 em `dano_no_piso`). Por isso o critério de desempate foi o comportamento ao vivo: na câmera, o modelo A da rodada 1 detectou a mesma lixeira com confiança 0,90, de forma estável, enquanto o C2 oscilava em torno de 0,26 e confundia a quina de uma estante com obstáculo.
8. **Avaliação.** Métricas no conjunto de teste (31 imagens de SP), por classe; matriz de confusão; desempenho separado entre SP (teste) e dataset aberto (reserva); análise dos piores casos.
9. **Tempo real.** O modelo roda em `src/tempo_real.py` sobre a webcam, a câmera do celular (via app de transmissão na mesma rede Wi-Fi) ou um vídeo gravado. Uma zona em forma de trapézio marca o chão logo à frente; se a base de uma caixa cai dentro dela, a zona fica vermelha e aparece o aviso. Com rastreamento, cada barreira recebe um ID e o trajeto termina com a contagem por tipo.
10. **Integração ao MVP.** O serviço `POST /detectar` recebe a foto do app, roda o detector na imagem original, pixela cabeças e placas (com um YOLO pré-treinado no COCO que acha pessoas e veículos) e devolve as detecções e a foto anonimizada. Se a maior confiança fica abaixo de 0,5, o relato vai para revisão humana antes de ser encaminhado.

## Exemplos de resultados

**Desempenho geral no teste, modelo final (YOLO26n, 3 classes, rodada 1)**

| Métrica | Valor |
| --- | ---: |
| Precisão | 0,48 |
| Recall | 0,14 |
| mAP50 | 0,16 |
| mAP50-95 | 0,08 |
| Velocidade na CPU do notebook (`tempo_real.py`, AMD Ryzen 5 2600, webcam) | 14,5 FPS (57 ms por quadro) |

**Por classe (teste):**

| Classe | Precisão | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| obstaculo | 0,57 | 0,28 | 0,30 | 0,17 |
| desnivel | 0,59 | 0,10 | 0,12 | 0,07 |
| buraco | 0,27 | 0,04 | 0,06 | 0,02 |

**Rodada 1, efeito da resolução (teste):** YOLO26n 640: mAP50 0,16, 11 FPS na CPU do Colab; YOLO26n 960: mAP50 0,15, 7 FPS. Aumentar a imagem não fez buraco e desnível aparecerem.

**Rodada 2, comparação de modelos (teste):**

| Modelo | Precisão | Recall | mAP50 | ms por imagem (GPU T4) |
| --- | ---: | ---: | ---: | ---: |
| YOLO26n, 3 classes (A) | 0,15 | 0,20 | 0,11 | 8,2 |
| YOLO26n, 2 classes (C2) | 0,27 | 0,21 | 0,17 | 4,1 |
| YOLO26s, 3 classes (B) | 0,40 | 0,16 | 0,17 | 5,6 |

O modelo small não superou o nano: com tão poucas imagens, o tamanho do modelo não é o gargalo.

**Velocidade na CPU:** 90 ms por imagem na CPU do Colab (11 FPS) e 14,5 FPS no notebook do grupo com a webcam (AMD Ryzen 5 2600, sem GPU).

**SP × dataset aberto (IA responsável):**

| Grupo | Imagens | Precisão | Recall | mAP50 |
| --- | ---: | ---: | ---: | ---: |
| São Paulo (teste) | 31 | 0,15 | 0,20 | 0,11 |
| Dataset aberto (reserva, nunca visto) | 16 | 0,94 | 0,83 | 0,89 |

(Modelo de 3 classes da rodada 2.) O mesmo modelo acerta muito mais nas imagens do dataset aberto, de outro país, com objetos grandes e fundo limpo, do que nas calçadas de São Paulo, com lixo, pisos variados e sombras. Um detector treinado só com dados prontos pareceria ótimo e falharia justamente onde vai ser usado.

**Figuras** (cada uma com legenda):
- Figura 1: curvas de treino (`results.png`).
- Figura 2: matriz de confusão normalizada.
- Figura 3: exemplos de acerto no teste (`exemplos_acerto.png`).
- Figura 4: quadro do tempo real com a zona de alerta acionada.
- Figura 5: resposta do `/detectar` com a foto anonimizada.

**Análise de erros:** cinco erros dos piores casos (`piores_casos.png`), cada um com o que aconteceu, a causa provável e a correção proposta.

| # | O que o modelo fez | Causa provável | Correção proposta |
| --- | --- | --- | --- |
| 1 | [ex.: não viu buraco coberto por folhas] | [poucos exemplos com folhas] | [mais imagens com folhas e chuva] |

## Conclusão

[Responder em 2 ou 3 parágrafos: o objetivo foi atingido em parte. O detector roda em tempo real (14,5 FPS) e acha obstáculos (mAP50 0,30), mas buraco (0,06) e desnível (0,12) não foram aprendidos com cerca de 110 exemplos de forma irregular, nem juntando as duas classes; a diferença entre SP (0,11) e dataset aberto (0,89) mostra que o gargalo são dados locais. Próximo passo: mais fotos de SP anotadas, em especial de dano no piso.]

**Limitações.** [Ex.: dano no piso não foi aprendido (forma irregular, poucos exemplos, caixas que não batem com IoU 0,5); teste pequeno (31 imagens), então diferenças de poucos centésimos entre modelos não são significativas; sem imagens a pé da periferia no Mapillary, o teste cobre só o centro, e o desempenho em calçadas da periferia não foi medido; imagens do Mapillary capturadas por terceiros, em datas variadas, e a calçada pode ter mudado desde então; poucas fotos noturnas e de chuva; classe `desnivel` confundida com sombra; anonimização por heurística, que pode deixar escapar um rosto muito pequeno.]

**Próximos passos.** Mais fotos enviadas pelos próprios cidadãos (com confirmação no app, viram novos rótulos); estimar o tamanho da barreira para priorizar; rodar o modelo no celular, sem internet; usar a câmera do robô vistoriador do Maker Lab.

## Referências

- Câmara Municipal de São Paulo. Subcomissão de Calçadas ouve responsável pelo serviço SP 156. 13/08/2026. https://www.saopaulo.sp.leg.br/blog/subcomissao-de-calcadas-ouve-responsavel-pelo-servico-sp-156/
- Portal Viva. Estudo da USP aponta que 88% das calçadas de SP são irregulares. 16/07/2026. https://viva.com.br/cidadania-e-direitos/estudo-da-usp-aponta-que-88-das-calcadas-de-sp-sao-irregulares.html
- Portal Viva. Queda em idosos não pode ser vista como normal. 24/06/2026. https://viva.com.br/saude-e-bem-estar/queda-em-idosos-nao-pode-ser-vista-como-normal-veja-cuidados-dentro-de-casa.html
- IBGE. Censo Demográfico 2022. https://biblioteca.ibge.gov.br/visualizacao/livros/liv102038.pdf
- Ultralytics. YOLO26 — documentação dos modelos. https://docs.ultralytics.com/models/
- Monte, D. M. F. M. do; Goldschmidt, R. R.; Santos, M. dos. Identificação e Classificação de Patologias em Pavimentos Rodoviários Flexíveis e Rígidos Utilizando YOLOv8. WebMedia, SBC. https://sol.sbc.org.br/index.php/webmedia/article/download/37973/37751
- Damaceno, R. J. P. et al. SideSeeing: a multimodal dataset and collection of tools for sidewalk assessment. arXiv:2407.06464. https://arxiv.org/abs/2407.06464
- Mapillary. CC BY-SA license for open data. https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- Mapillary. Image privacy. https://help.mapillary.com/hc/en-us/articles/115001770349
- Roboflow. Preprocess Images (Modify Classes). https://docs.roboflow.com/datasets/dataset-versions/image-preprocessing
- Blindspot. Sidewalk obstacles Dataset. Roboflow Universe, 2023. https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles
