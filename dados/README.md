# Dados

As imagens não ficam no Git: elas moram no projeto do Roboflow e são baixadas pelos notebooks.

- **Projeto no Roboflow:** https://universe.roboflow.com/pedros-workspace-md4aw/passo-firme-calcadas (workspace `pedros-workspace-md4aw`, projeto `passo-firme-calcadas`)
- **Versão usada no modelo final:** 1, `v1-sp-blindspot` (imagens de SP do Mapillary + Sidewalk obstacles), com Auto-Orient, sem Resize e sem aumento de dados no Roboflow (o aumento é feito no treino)

Para rodar os scripts localmente, baixe a versão no formato YOLO (`yolov8`) para `dados/<nome>/` e use o `data.yaml` que vem junto. O `data.yaml.exemplo` mostra a forma esperada.

## Composição da versão 1

| Conjunto | Imagens | Sem barreira | buraco | desnivel | obstaculo |
| --- | ---: | ---: | ---: | ---: | ---: |
| Treino | 216 | 21 | 58 | 52 | 463 |
| Validação | 38 | 1 | 5 | 17 | 90 |
| Teste (só SP) | 31 | 5 | 25 | 10 | 36 |

Contagem de caixas por classe, tirada da saída do notebook da rodada 1.

## Datasets abertos usados

| Dataset | Link | Licença | Imagens usadas | Classes de origem → nossas |
| --- | --- | --- | ---: | --- |
| Sidewalk obstacles (Blindspot) | https://universe.roboflow.com/blindspot-fmcu0/sidewalk-obstacles | CC BY 4.0 | 105 | pole, warning_column, reflective_cone, spherical_roadblock, ashcan, fire_hydrant e as classes de nome numérico que marcam obstáculos (`000000005669`, `5326`, `5620`, `5336`, `5967`) → obstaculo; pessoas, veículos e placas (incluindo `000000002782`, `1589`, `4968`, `2258`, `2687`) descartados |

As classes com nome de número são rótulos trocados no dataset original; cada uma foi identificada olhando as imagens.

As 105 imagens foram clonadas no Roboflow (*Clone Images*) só para treino e validação: o teste tem apenas imagens de São Paulo.

## Imagens de São Paulo (Mapillary)

180 imagens de calçadas da região da Sé, no centro (149 de treino e validação e 31 de teste depois da revisão), baixadas com `scripts/baixar_mapillary.py`: só sequências capturadas a pé (velocidade mediana de 0,5 a 2,2 m/s, pico de até 3,5 m/s e no máximo 30% do tempo parado, o que barra carros no trânsito), no máximo 8 imagens por sequência, com pelo menos 8 m entre elas. Nomes no padrão `sp_<bairro>_<id>.jpg`.

- **Divisão por sequência:** as 180 imagens vêm de 27 sequências; 23 ficaram em treino e validação e 4 inteiras no teste, sem nenhuma sequência nos dois lados.
- **Viés conhecido:** todas as 180 são do mesmo colaborador do Mapillary, tiradas numa mesma data, de dia, na mesma região. Nos bairros da periferia testados (Itaquera e Jabaquara), nenhuma sequência passou no filtro de captura a pé.
- **Licença:** as imagens continuam sob CC BY-SA 4.0 e entram no dataset sem alteração. O projeto no Roboflow está em CC BY 4.0, que vale para as anotações do grupo.
- **Créditos:** `creditos_mapillary.csv` (cópia do `creditos.csv` gerado pelo script), com autor, data, sequência e link de cada imagem. Ele lista as 250 imagens baixadas; as 180 usadas são as que estão no dataset (as demais não mostravam calçada e foram descartadas na revisão).
- **Privacidade:** o Mapillary borra rostos e placas automaticamente; mesmo assim, cada imagem foi revisada antes do upload.
