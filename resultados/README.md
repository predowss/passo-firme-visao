# Resultados

Figuras e tabelas que vão para o README principal e para o PDF. Todas vêm do modelo final (YOLO26n, 3 classes, 640 px, rodada 1).

- `A_yolo26n/results.png`: curvas de treino do experimento A
- `A_teste/confusion_matrix_normalized.png`: matriz de confusão no teste (31 fotos de São Paulo)
- `exemplos_acerto.png` e `piores_casos.png`: painéis de acertos e erros no teste
- `limiares.csv`: precisão e recall no teste em 4 limiares de confiança (0,10, 0,25, 0,35 e 0,50), com IoU de 0,5 e de 0,3, por classe e por foto; saída do `notebooks/03_limiar_confianca_colab.ipynb`
- `tempo_real_modeloA.jpeg`: o `tempo_real.py` na webcam do PC (lixeira com 0,89; 14,3 FPS na tela, 14,5 FPS de média)
- `tempo_real_celular.jpg`: o `tempo_real.py` com a câmera do celular pelo Wi-Fi (DroidCam), em 16/11: lixeira com 0,87, zona de alerta acionada, cerca de 11 FPS
- `tempo_real_ao_vivo.gif`: 6,5 s da detecção ao vivo pela câmera do celular (lixeira e zona de alerta), para o README
- `fluxo.png`: diagrama do fluxo do componente (dados, treino, avaliação e uso do modelo), Figura 1 do relatório
- `detectar_resposta_caixas.jpg`: resposta do `/detectar` desenhada na foto, com três obstáculos e a cabeça e as placas pixeladas

Vídeos `.mp4` não entram no Git (estão no `.gitignore`); o vídeo de entrega vai para o YouTube.
