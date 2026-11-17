# Modelos

`best.pt` é o modelo final do projeto: YOLO26n ajustado a partir dos pesos do COCO para 3 classes (`buraco`, `desnivel` e `obstaculo`), com imagens de 640 px. É o experimento A da rodada 1 (`notebooks/01_treino_yolo26_colab.ipynb`), escolhido depois da comparação com a rodada 2 (detalhes no relatório). Tem 5,5 MB e fica versionado no Git.

Quem usa este arquivo: `src/tempo_real.py`, o serviço `src/api.py`, o `Dockerfile` e o `notebooks/03_limiar_confianca_colab.ipynb`, que o baixa direto do GitHub.

O YOLO26n do COCO usado só na anonimização (`yolo26n.pt`) é baixado pelo Ultralytics na primeira execução e não entra no Git. Para trocar de modelo, baixe o `best.pt` no fim de um notebook de treino (seção 9) e substitua este, com o mesmo nome.

Licença: o modelo foi treinado com a biblioteca Ultralytics, distribuída sob AGPL-3.0, e segue essa licença.
