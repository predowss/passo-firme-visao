# Dados

As imagens não ficam no Git: elas moram no projeto do Roboflow e são baixadas pelo notebook.

- **Projeto no Roboflow:** [link público do projeto]
- **Versão usada no modelo final:** [número] (datasets abertos + fotos próprias)
- **Versão só com datasets abertos (experimento C):** [número]

Para rodar os scripts localmente, baixe a versão no formato YOLO (`yolov8`) para `dados/<nome>/` e use o `data.yaml` que vem junto. O `data.yaml.exemplo` mostra a forma esperada.

## Datasets abertos usados

| Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
| --- | --- | --- | ---: | --- |
| [nome] | [link] | [licença] | [N] | [ex.: pothole → buraco] |

## Fotos próprias

[N] fotos de calçadas de [bairros], tiradas pelo grupo entre [datas], com rostos e placas pixelados antes do upload. Nomes no padrão `sp_<bairro>_<número>.jpg`.
