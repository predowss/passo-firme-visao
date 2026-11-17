# Roteiro do vídeo de demonstração (até 5 pontos)

O vídeo prova que a solução funciona: o detector rodando de verdade, em casa ao vivo e numa calçada real, não slides. Alvo: 3 a 4 minutos. Publiquem no YouTube como **não listado** e testem o link numa janela anônima.

O modelo final (YOLO26n, 3 classes) acha bem **obstáculos**: postes, sacos e montes de lixo, lixeiras, cones, entulho. Buraco e desnível ainda falham. O trajeto da gravação deve passar por obstáculos; se um buraco for detectado, ótimo, mas não forcem.

**Como o vídeo é montado.** O modelo roda num PC de mesa, que não sai de casa. Por isso a demonstração tem duas partes:

1. **Ao vivo, em casa:** o celular manda a câmera para o PC pelo Wi-Fi (DroidCam) e o PC detecta em tempo real, a cerca de 12 quadros por segundo. Gravado em 16/11: robô aspirador com até 0,88 e lixeira com 0,85 a 0,87, com a zona vermelha.
2. **Na calçada:** a caminhada é filmada com a câmera normal do celular e processada depois no PC, quadro a quadro, pelo mesmo script. Sem a marca d'água do DroidCam e com imagem melhor. Gravada em 17/11 no Centro de Osasco, cidade que o modelo não viu no treino: cones, cadeiras de plástico, sacos de lixo, vasos e postes, com a zona vermelha.

## Montagem (cerca de 3 min 50 s)

| Tempo | Cena | Imagem | Arquivo |
| --- | --- | --- | --- |
| 0:00–0:15 | Abertura | Cartela de abertura sobre a calçada filmada | `video_edicao/cartelas/01_abertura.png` + `video_edicao/fotos_rua/1000335644_piso_buracos.jpg` ou `1000335651_desnivel_cone.jpg` (zoom lento) |
| 0:15–0:30 | O problema | Cartela com os números do SP156 | `video_edicao/cartelas/02_problema.png` |
| 0:30–0:55 | Dados e treino | Cartela dos dados; depois o diagrama do fluxo | `video_edicao/cartelas/03_dados_treino.png`, `resultados/fluxo.png` |
| 0:55–1:25 | Ao vivo, em casa | Detecção ao vivo pela câmera do celular | `ao_vivo_trecho.mp4` (27 s) |
| 1:25–2:15 | Na calçada (a parte mais importante) | A caminhada processada e anonimizada; se sobrar tempo, as fotos de teste de SP com detecção | `video_edicao/rua_cortes_anonimo.mp4` (33 s) e, opcional, `video_edicao/calcadas_sp_detectado.mp4` (20 s, anonimizar antes) |
| 2:15–2:45 | Serviço do app | O `/docs` com a resposta e a foto anonimizada | `docs_trecho.mp4` (27 s) |
| 2:45–3:00 | Resultados | Cartela com 0,30, 81% e 12–14 FPS | `video_edicao/cartelas/04_resultados.png` |
| 3:00–3:35 | IA responsável e limites | Cartela 0,89 × 0,11; o cachorro sem alerta; a tampa de bueiro marcada como buraco; cartela dos limites | `video_edicao/cartelas/05_ia_responsavel.png`, `ao_vivo_limite_cachorro.mp4`, `video_edicao/rua_limite_bueiro_anonimo.mp4` (5 s), `video_edicao/cartelas/06_limites.png` |
| 3:35–3:50 | Fechamento | Nomes, RMs e link do repositório | `video_edicao/cartelas/07_fechamento.png` |

## Texto da narração

Cerca de 400 palavras: lidas com calma (uns 145 por minuto), dão 2 min 45 s de fala; o resto do tempo é imagem, com som ambiente ou música baixa. O texto serve também como legenda.

**0:00–0:15 · Abertura.** "Andar a pé é o primeiro e o último trecho de qualquer deslocamento. Para um idoso ou uma pessoa com deficiência, um buraco ou um obstáculo na calçada pode significar uma queda, ou ficar em casa."

**0:15–0:30 · O problema.** "Em São Paulo, os pedidos de conserto de calçada ao SP156 chegaram a 49 mil em 2025, com 33 dias de espera média. Falta saber onde estão as barreiras e quais são mais graves."

**0:30–0:55 · Dados e treino.** "O Passo Firme usa visão computacional para isso. Treinamos um YOLO26n sob medida, partindo dos pesos do COCO, com 180 fotos de calçadas de São Paulo tiradas a pé e 105 imagens de um dataset aberto. Anotamos três classes, buraco, desnível e obstáculo, e separamos o teste por sequência, só com ruas de São Paulo."

**0:55–1:25 · Ao vivo.** "Aqui, o celular manda a câmera para o computador pelo Wi-Fi, e o modelo roda em tempo real, a 12 quadros por segundo, só na CPU, sem placa de vídeo. Quando uma barreira entra na faixa à frente de quem anda, a zona fica vermelha e o aviso aparece. Cada barreira ganha um número e entra na contagem do trajeto."

**1:25–2:15 · Na calçada.** *Com a caminhada:* "Agora, uma calçada de verdade, no Centro de Osasco, uma cidade que o modelo nunca viu no treino. Filmamos o trajeto, e o mesmo modelo processou o vídeo quadro a quadro. Cones, cadeiras, sacos de lixo, vasos e postes no caminho são marcados como obstáculos, e a zona fica vermelha quando eles entram na faixa à frente. O contador no alto soma as barreiras distintas do trajeto: é essa contagem que vira o mapa de prioridades do Passo Firme." *Se usarem também o plano B:* "Estas são fotos de calçadas do centro de São Paulo que o modelo nunca viu no treino. Ele marca os obstáculos, como sacos de lixo, cones e entulho, e às vezes erra: barreiras pequenas e distantes e defeitos do piso ainda escapam."

**2:15–2:45 · Serviço do app.** "No aplicativo, a foto do cidadão vai para o serviço de detecção. Ele endireita a foto, devolve cada barreira com a confiança, aqui três obstáculos, e pixela rostos e placas antes de a foto ser guardada. Se o modelo não tiver certeza, uma pessoa revisa antes de encaminhar."

**2:45–3:00 · Resultados.** "No teste, o modelo chega a 0,30 de mAP50 em obstáculos, e 81% das fotos com barreira recebem pelo menos uma detecção. As outras vão para revisão humana."

**3:00–3:35 · IA responsável e limites.** "Um modelo igual acerta 0,89 em imagens do dataset aberto e só 0,11 nas ruas de São Paulo: dado local faz diferença. E ele só reconhece o que viu no treino: este cachorro deitado no caminho passou sem alerta. Na rua, confundiu uma tampa de bueiro com buraco e só viu a caixa aberta ao lado quando já estava em cima dela. Buraco e desnível ainda precisam de mais exemplos."

**3:35–3:50 · Fechamento.** "O próximo passo é usar as fotos dos próprios cidadãos como novos exemplos, de vários bairros. Passo Firme: o olho que mapeia as barreiras da calçada."

## Já gravado e pronto (16 e 17/11)

- `ao_vivo_trecho.mp4` (27 s): robô aspirador e lixeira detectados, zona vermelha, 11,5 a 12,7 FPS na tela.
- `ao_vivo_limite_cachorro.mp4` (7 s): cachorro deitado no meio da zona, sem alerta.
- `docs_trecho.mp4` (27 s): o `/docs` com zoom na resposta e a foto anonimizada no fim.
- `video_edicao/cartelas/`: as 7 cartelas em 1920×1080 (abertura, problema, dados e treino, resultados, IA responsável, limites, fechamento).
- Plano B da calçada, já processado: `video_edicao/calcadas_sp_detectado.mp4` (20 s), com 8 fotos de teste de SP que o modelo nunca viu: saco de lixo (0,90) e cone com a zona vermelha, carroça, postes, "buraco à frente" em piso danificado e, no fim, um erro honesto (lixo miúdo sobre pedra portuguesa, sem detecção). O vídeo completo com as 31 fotos está em `resultados/sp_teste_detectado.mp4`. Antes de publicar, passem pelo `anonimizar_video.py`.
- Rua, 17/11 (pasta `video_edicao/`): `rua_cortes_anonimo.mp4` (33 s, já anonimizado): cones e cadeiras de plástico com alerta, sacos de lixo em volta do poste, saco (0,9) e vaso com alerta, poste com bicicletas, aproximação do saco ao lado do poste. `rua_limite_bueiro_anonimo.mp4` (5 s, anonimizado): tampa de bueiro marcada como buraco; a caixa aberta ao lado só é marcada no fim, já colada. A caminhada inteira processada está em `resultados/demo_rua.mp4` (183 s, sem anonimizar: não publicar) e as fotos aproveitáveis em `fotos_rua/`.
- Para a cena do `/docs`, fica o `docs_trecho.mp4`, com a foto de teste `sp_se_1542016304509302.jpg`. A foto da rua `1000335654_sacos_pessoa_placa.jpg` não serve: testada em 17/11, os sacos grandes e próximos não foram marcados; o único obstáculo (0,31) foi o cachorro ao fundo e, com recortes, entrou um falso "buraco" (0,42) num tufo de mato. A foto foi para revisão humana.
- Na gravação ao vivo completa, evitem o começo e o trecho de 1:45 a 1:58 (brinquedo de personagem de desenho) e o falso alerta na quina da porta (~1:40).

## Parte 1: ao vivo, em casa

1. **Celular e PC no mesmo Wi-Fi.** Abram o DroidCam no celular e anotem o IP que ele mostra (em 16/11 era `192.168.0.14`). Não abram o endereço no navegador nem o programa do DroidCam no PC: a versão grátis aceita uma conexão por vez.
2. Rodem, trocando o IP se tiver mudado:
   `py src\tempo_real.py --modelo modelos\best.pt --fonte http://192.168.0.14:4747/video --rastrear`
   Se não abrir, troquem `/video` por `/mjpegfeed`. Se der erro sobre o pacote `lap`, rodem `py -m pip install lap`.
3. **Gravem a janela com Win + Alt + R** (Xbox Game Bar), com a janela do Passo Firme clicada e na frente. Também dá para usar `--salvar` ao vivo: o script mede o FPS real (uns 12 quadros por segundo pela rede) e grava com ele, então o arquivo toca na velocidade certa.
4. Uma segunda pessoa filma, com outro celular, quem anda pela casa (para a tela dividida). Passem devagar pela lixeira e por outro objeto no chão; parem 2 a 3 segundos diante de cada um.
5. A marca "using droidcam.app" no meio da imagem é da versão grátis; pode ficar.

## Parte 2: na calçada (feita em 17/11)

1. Com luz do dia (de preferência entre 10h e 15h), numa calçada com obstáculos.
2. **Câmera normal do celular, na horizontal, em 1080p e 30 quadros por segundo** (nas configurações da câmera; 4K ou 60 quadros deixam o processamento bem mais lento).
3. Celular na altura do peito, apontado para a calçada à frente, um pouco para baixo. Andem devagar e parem 2 a 3 segundos diante de cada obstáculo.
4. Esperem os pedestres passarem; ninguém de fora do grupo com o rosto identificável.
5. Se der, a segunda pessoa filma quem anda, para mostrar a calçada de fora.
6. **Em casa:** passem o vídeo para o PC (cabo USB ou Quick Share), salvem como `caminhada.mp4` na pasta do repositório e rodem:
   `py src\tempo_real.py --modelo modelos\best.pt --fonte caminhada.mp4 --rastrear --salvar resultados\demo_rua.mp4`
   O PC processa todos os quadros, então o `demo_rua.mp4` sai na velocidade normal, mesmo que o FPS da tela mostre uns 11 a 14. Os `.mp4` não vão para o GitHub (estão no `.gitignore`).

## Parte 3: o `/docs`, em casa

`py -m uvicorn src.api:app --port 8001`, abrir `localhost:8001/docs` e gravar a tela com **Win + Alt + R**. Usem a foto `mapillary_sp\teste\sp_se_1542016304509302.jpg`, com `devolver_imagem` em false.

## Depois da gravação

1. **Anonimizar antes de publicar** (cabeças e placas) o vídeo da calçada e o do segundo celular:
   `py scripts\anonimizar_video.py resultados\demo_rua.mp4 resultados\demo_rua_anonimo.mp4`
   A gravação de casa só precisa passar pelo script se aparecer alguém de fora do grupo.
2. Editar (CapCut, DaVinci Resolve ou Clipchamp, que já vem no Windows): tela dividida, legendas e os trechos do `/docs` e dos resultados.
3. Publicar no YouTube como não listado e colar o link no README e no PDF.

## Checklist do vídeo

- [ ] O detector aparece funcionando ao vivo, com o FPS visível.
- [x] O detector aparece numa calçada real (Centro de Osasco, 17/11).
- [x] Pelo menos três obstáculos diferentes detectados (cones, cadeiras, sacos de lixo, vasos, postes).
- [ ] A zona de alerta fica vermelha pelo menos uma vez.
- [ ] Uma foto passa pelo `/detectar` e volta anonimizada.
- [ ] Os limites aparecem com honestidade (buraco e desnível; São Paulo × dataset aberto; objeto fora do treino).
- [x] Vídeos da rua passados pelo `anonimizar_video.py` (conferido em quadros); ninguém de fora do grupo identificável.
- [ ] Legendas ligadas ou embutidas.
- [ ] Link testado numa janela anônima.
