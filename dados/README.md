# Dados

As imagens não ficam no Git: elas moram no projeto do Roboflow e são baixadas pelo notebook.

- **Projeto no Roboflow:** [link público do projeto]
- **Versão usada no modelo final:** [número] (imagens de SP do Mapillary + Sidewalk obstacles)

Para rodar os scripts localmente, baixe a versão no formato YOLO (`yolov8`) para `dados/<nome>/` e use o `data.yaml` que vem junto. O `data.yaml.exemplo` mostra a forma esperada.

## Datasets abertos usados

| Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
| --- | --- | --- | ---: | --- |
| Sidewalk obstacles (Blindspot) | https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles | CC BY 4.0 | 105 | pole, warning_column, reflective_cone, spherical_roadblock, ashcan, fire_hydrant e as classes de nome numérico que marcam obstáculos (`000000005669`, `5326`, `5620`, `5336`, `5967`) → obstaculo; pessoas, veículos e placas (incluindo `000000002782`, `1589`, `4968`, `2258`, `2687`) descartados |

As classes com nome de número são rótulos trocados no dataset original; cada uma foi identificada olhando as imagens.

As 105 imagens foram clonadas no Roboflow (*Clone Images*) só para treino e validação: o teste tem apenas imagens de São Paulo.

## Imagens de São Paulo (Mapillary)

[N] imagens de calçadas de [bairros] (149 de treino e validação e 32 de teste depois da revisão), baixadas com `scripts/baixar_mapillary.py`: só sequências capturadas a pé (velocidade mediana de 0,5 a 2,2 m/s, pico de até 3,5 m/s e no máximo 30% do tempo parado, o que barra carros no trânsito), no máximo 8 imagens por sequência, com pelo menos 8 m entre elas. Nomes no padrão `sp_<bairro>_<id>.jpg`.

- **Licença:** as imagens continuam sob CC BY-SA 4.0 e entram no dataset sem alteração (sem Resize nem aumento de dados no Roboflow). O projeto no Roboflow está em CC BY 4.0, que vale para as anotações do grupo.
- **Créditos:** `creditos_mapillary.csv` (cópia do `creditos.csv` gerado pelo script), com autor, data e link de cada imagem.
- **Privacidade:** o Mapillary borra rostos e placas automaticamente; mesmo assim, cada imagem foi revisada antes do upload.
