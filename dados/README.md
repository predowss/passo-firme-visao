# Dados

As imagens não ficam no Git: elas moram no projeto do Roboflow e são baixadas pelo notebook.

- **Projeto no Roboflow:** [link público do projeto]
- **Versão usada no modelo final:** [número] (datasets abertos + imagens de SP do Mapillary)
- **Versão só com datasets abertos (experimento C):** [número]

Para rodar os scripts localmente, baixe a versão no formato YOLO (`yolov8`) para `dados/<nome>/` e use o `data.yaml` que vem junto. O `data.yaml.exemplo` mostra a forma esperada.

## Datasets abertos usados

| Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
| --- | --- | --- | ---: | --- |
| [nome] | [link] | [licença] | [N] | [ex.: pothole → buraco] |

## Imagens de São Paulo (Mapillary)

[N] imagens de calçadas de [bairros], baixadas com `scripts/baixar_mapillary.py`: só sequências capturadas a pé (0,3 a 2,5 m/s), no máximo 12 imagens por sequência, com pelo menos 8 m entre elas. Nomes no padrão `sp_<bairro>_<id>.jpg`.

- **Licença:** as imagens continuam sob CC BY-SA 4.0 e entram no dataset sem alteração (sem Resize nem aumento de dados no Roboflow). O projeto no Roboflow está em CC BY 4.0, que vale para as anotações do grupo.
- **Créditos:** `creditos_mapillary.csv` (cópia do `creditos.csv` gerado pelo script), com autor, data e link de cada imagem.
- **Privacidade:** o Mapillary borra rostos e placas automaticamente; mesmo assim, cada imagem foi revisada antes do upload.
