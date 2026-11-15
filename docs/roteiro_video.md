# Roteiro do vídeo de demonstração (até 5 pontos)

O vídeo prova que a solução funciona: mostrem o detector rodando de verdade, não slides. Alvo: 3 a 4 minutos. Publiquem no YouTube como **não listado** e testem o link numa janela anônima.

| Tempo | Cena | O que aparece | Fala (resumo) |
| --- | --- | --- | --- |
| 0:00–0:20 | Problema | Imagens reais de uma calçada com buraco e placa levantada | "Em SP, pedidos de conserto de calçada esperam 33 dias em média. Quem mais sofre são idosos e pessoas com deficiência." |
| 0:20–0:50 | Dados e treino | Roboflow com as anotações; Colab com `results.png` e a tabela por classe | "Juntamos datasets abertos e [N] imagens de calçadas de São Paulo do Mapillary, anotamos 3 classes e treinamos um YOLO26n. No teste: mAP50 de [X] e recall de [X]." |
| 0:50–2:20 | Tempo real (a parte mais importante) | Tela dividida: à esquerda, quem filma andando na calçada; à direita, o notebook com caixas, FPS e a zona ficando vermelha | "O celular transmite a câmera para o notebook. Quando uma barreira entra na faixa à frente, o aviso aparece." Parem diante de cada tipo de barreira. |
| 2:20–2:50 | Integração com o app | `/docs` do serviço (ou o app do Passo Firme): enviar uma foto, ver o JSON e a foto com rostos e placas pixelados | "No app, a foto do cidadão vira detecção. Rostos e placas saem borrados, e casos incertos vão para revisão humana." |
| 2:50–3:30 | Resultados e limites | Tabela periferia × centro; um erro típico | "O modelo erra mais com [X]. Próximo passo: mais fotos de chuva e noite." |
| 3:30–3:45 | Fechamento | Nomes e RMs na tela | "Passo Firme: o olho que mapeia as barreiras da calçada." |

## Como gravar o tempo real

1. Instalem no celular um app que transmita a câmera pela rede Wi-Fi (ex.: IP Webcam, no Android) ou que faça o celular virar webcam do computador (ex.: DroidCam). No Mac com iPhone, a Câmera de Continuidade aparece direto como webcam.
2. Celular e notebook na mesma rede. Um roteador do celular (hotspot) resolve na rua.
3. Rodem:
   `python src/tempo_real.py --modelo modelos/best.pt --fonte <URL ou número da câmera> --rastrear --salvar resultados/demo.mp4`
4. Gravem a tela com o OBS Studio, e outra pessoa filma quem anda (para a tela dividida).
5. Plano B: gravem antes um vídeo andando na calçada e rodem o script sobre ele. Digam no vídeo que é um vídeo gravado processado quadro a quadro, com o FPS na tela.

## Checklist do vídeo

- [ ] O detector aparece funcionando numa calçada real, com o FPS visível.
- [ ] Aparecem as três classes pelo menos uma vez.
- [ ] A zona de alerta aciona pelo menos uma vez.
- [ ] Uma foto passa pelo `/detectar` e volta anonimizada.
- [ ] Ninguém de fora do grupo aparece com o rosto identificável.
- [ ] Legendas ligadas ou embutidas.
- [ ] Link testado numa janela anônima.
