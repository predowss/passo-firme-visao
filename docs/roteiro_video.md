# Roteiro do vídeo de demonstração (até 5 pontos)

O vídeo prova que a solução funciona: o detector rodando de verdade numa calçada, não slides. Alvo: 3 a 4 minutos. Publiquem no YouTube como **não listado** e testem o link numa janela anônima.

O modelo final (YOLO26n, 3 classes) acha bem **obstáculos**: postes, sacos e montes de lixo, lixeiras, cones, entulho. Buraco e desnível ainda falham. O trajeto da gravação deve passar por obstáculos; se um buraco for detectado, ótimo, mas não forcem.

| Tempo | Cena | O que aparece | Fala (resumo) |
| --- | --- | --- | --- |
| 0:00–0:20 | Problema | Calçada real filmada pelo grupo: lixo no caminho, poste no meio, piso quebrado | "Em São Paulo, os pedidos de conserto de calçada passaram de 49 mil em 2025 e esperam, em média, 33 dias. Quem mais sofre são idosos e pessoas com deficiência." |
| 0:20–0:55 | Dados e treino | Roboflow com as anotações; `results.png` e a tabela de teste no Colab | "Usamos 180 fotos de calçadas de São Paulo do Mapillary, tiradas a pé, e 105 de um dataset aberto. Anotamos buraco, desnível e obstáculo e fizemos o ajuste fino de um YOLO26n. No teste, só com ruas de São Paulo, o mAP50 foi de 0,16 no geral e 0,30 em obstáculos." |
| 0:55–2:25 | Tempo real (a parte mais importante) | Tela dividida: de um lado, quem anda com o celular; do outro, o notebook com caixas, FPS e a zona ficando vermelha | "O celular manda a câmera para o notebook, que roda o modelo a 14 quadros por segundo, só na CPU. Quando um obstáculo entra na faixa à frente, a zona fica vermelha e o aviso aparece." Parem 2 a 3 segundos diante de cada obstáculo. |
| 2:25–2:55 | Serviço do app | `/docs` do serviço: enviar a foto do saco de lixo, ver o JSON e a foto com a cabeça e as placas pixeladas | "No app, a foto do cidadão vira detecção: três obstáculos, com a confiança de cada um. Rostos e placas saem pixelados antes de a foto ser guardada, e casos sem certeza vão para revisão humana." |
| 2:55–3:35 | Resultados e limites | Tabela São Paulo × dataset aberto; o painel `piores_casos.png` | "Um modelo igual acerta 0,89 em fotos do dataset aberto que não viu e só 0,11 nas ruas de São Paulo: dado local faz diferença. Buraco e desnível ainda não foram aprendidos com cerca de 110 exemplos. O próximo passo é anotar mais fotos de São Paulo." |
| 3:35–3:50 | Fechamento | Nomes e RMs na tela | "Passo Firme: o olho que mapeia as barreiras da calçada." |

## Antes de sair de casa

1. **Câmera do celular no notebook.** No DroidCam, prefiram o **cabo USB** (mais estável na rua que o Wi-Fi): no celular, *Ativar depuração USB* nas opções do desenvolvedor; no programa do PC, conectar por USB. Testem:
   `py src\tempo_real.py --modelo modelos\best.pt --fonte 1 --rastrear`
   Se der erro sobre o pacote `lap`, rodem `py -m pip install lap`.
2. **Bateria:** notebook e celular carregados; levem o carregador e o cabo.
3. **Segunda câmera:** outra pessoa filma, com o próprio celular, quem anda (para a tela dividida).
4. **Gravar o trecho do `/docs` em casa:** `py -m uvicorn src.api:app --port 8001`, abrir `localhost:8001/docs` e gravar a tela com **Win + Alt + R** (Xbox Game Bar). Usem a foto `mapillary_sp\teste\sp_se_1542016304509302.jpg`, com `devolver_imagem` em false.

## Na rua

1. Com luz do dia (de preferência entre 10h e 15h), numa calçada com obstáculos.
2. Rodem gravando o vídeo anotado:
   `py src\tempo_real.py --modelo modelos\best.pt --fonte 1 --rastrear --salvar resultados\demo.mp4`
3. Celular na altura do peito, apontado para a calçada à frente, um pouco para baixo. Andem devagar e parem diante de cada obstáculo.
4. Esperem os pedestres passarem; ninguém de fora do grupo com o rosto identificável.
5. Tecla **q** para encerrar; o script imprime o FPS médio.

**Plano B:** se o ao vivo falhar, filmem o trajeto com o celular e rodem o modelo sobre o arquivo:
`py src\tempo_real.py --modelo modelos\best.pt --fonte caminhada.mp4 --rastrear --salvar resultados\demo.mp4`
Digam no vídeo que é um vídeo gravado, processado quadro a quadro, com o FPS na tela.

## Depois da gravação

1. **Anonimizar antes de publicar** (cabeças e placas), tanto o vídeo do notebook quanto o do segundo celular:
   `py scripts\anonimizar_video.py resultados\demo.mp4 resultados\demo_anonimo.mp4`
2. Editar (CapCut, DaVinci Resolve ou Clipchamp, que já vem no Windows): tela dividida, legendas e os trechos do `/docs` e dos resultados.
3. Publicar no YouTube como não listado e colar o link no README e no PDF.

## Checklist do vídeo

- [ ] O detector aparece funcionando numa calçada real, com o FPS visível.
- [ ] Pelo menos três obstáculos diferentes detectados (ex.: poste, lixo, cone).
- [ ] A zona de alerta fica vermelha pelo menos uma vez.
- [ ] Uma foto passa pelo `/detectar` e volta anonimizada.
- [ ] Os limites aparecem com honestidade (buraco e desnível; São Paulo × dataset aberto).
- [ ] Vídeos passados pelo `anonimizar_video.py`; ninguém de fora do grupo identificável.
- [ ] Legendas ligadas ou embutidas.
- [ ] Link testado numa janela anônima.
