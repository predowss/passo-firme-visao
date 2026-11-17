# Modelos

`best.pt` é o modelo final do projeto: YOLO26n ajustado a partir dos pesos do COCO para 3 classes (`buraco`, `desnivel` e `obstaculo`), com imagens de 640 px. É o experimento A da rodada 1 (`notebooks/01_treino_yolo26_colab.ipynb`), escolhido depois da comparação com a rodada 2 (detalhes no relatório). Tem 5,5 MB e fica versionado no Git.

Quem usa este arquivo: `src/tempo_real.py`, o serviço `src/api.py`, o `Dockerfile` e os notebooks `03_limiar_confianca_colab.ipynb` e `04_melhorias_sem_novos_dados_colab.ipynb`, que o baixam direto do GitHub.

O notebook 04 também treinou uma variante com treino e validação juntos (E4, `best_trainval.pt`). Ela não superou este modelo no teste (mAP50 de 0,157 contra 0,175, na mesma conta) e não foi adotada nem versionada.

O YOLO26n do COCO usado só na anonimização (`yolo26n.pt`) é baixado pelo Ultralytics na primeira execução e não entra no Git. Para trocar de modelo, baixe o `best.pt` no fim de um notebook de treino (seção 9) e substitua este, com o mesmo nome.

Licença: o modelo foi treinado com a biblioteca Ultralytics, distribuída sob AGPL-3.0, e segue essa licença.
