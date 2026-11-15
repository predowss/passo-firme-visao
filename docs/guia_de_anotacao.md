# Guia de coleta e anotação — Passo Firme

Todo mundo que revisa ou anota imagens segue este guia. Anotação inconsistente (um anota a placa quebrada inteira, outro só a borda) derruba o mAP mais do que qualquer ajuste de treino.

## 1. Classes

| Classe | Anote | Não anote |
| --- | --- | --- |
| `buraco` | Buraco, afundamento ou pedaço faltando no piso da calçada | Tampa de bueiro fechada; junta fina entre placas; mancha ou sombra |
| `desnivel` | Degrau no meio da calçada, placa levantada, raiz erguendo o piso, borda quebrada que faz tropeçar | Rampa regular; guia (meio-fio) entre calçada e rua; degrau de entrada de imóvel fora da faixa de passagem |
| `obstaculo` | Objeto que estreita a passagem: poste, lixeira, entulho, mesa ou cadeira de comércio, placa, tapume, galho baixo | Objeto encostado no muro que não bloqueia; pessoas; animais |
| `veiculo_na_calcada` (opcional) | Carro ou moto parado em cima da calçada | Veículo na rua, mesmo encostado na guia |

A quarta classe só entra no treino com pelo menos 80 exemplos anotados.

## 2. Regras da caixa

No Roboflow, usem a ferramenta *Bounding Box* (quadrado na barra da direita, tecla **B**), não o *Smart Polygon*. Ao fechar a caixa, digitem o nome da classe exatamente como na tabela, sem acento.


1. **Caixa justa** em volta da barreira, sem sobra de chão limpo.
2. **Uma caixa por barreira.** Várias placas quebradas emendadas = uma caixa só; dois buracos separados por piso bom = duas caixas.
3. **Parcialmente visível:** anote se dá para ver pelo menos um terço da barreira.
4. **Longe demais:** não anote o que estiver a mais de uns 10 metros ou menor que um polegar na tela do celular. O modelo não precisa achar o que o pedestre ainda não alcança.
5. **Na dúvida entre duas classes**, use a que descreve o risco para quem anda: buraco com borda alta é `buraco`; placa levantada sem buraco é `desnivel`.
6. **Na dúvida se é barreira**, não anote e deixe a foto de fora. Foto com barreira sem anotação ensina o modelo a ignorá-la.
7. **Fotos sem barreira nenhuma** (calçada boa) entram como imagem vazia (*null*). Mantenham perto de 10% do total: ensinam o modelo a não inventar barreira.

## 3. Imagens de São Paulo (Mapillary)

As imagens de calçadas de São Paulo vêm do Mapillary, filtradas para sequências capturadas a pé.

1. **Token.** Crie uma conta em mapillary.com, registre um app na área de desenvolvedores e copie o *Client Token* (começa com `MLY|`).
2. **Baixar.** No Prompt de Comando, dentro da pasta do repositório (as aspas são obrigatórias por causa do `|`):

   ```cmd
   set "MAPILLARY_TOKEN=MLY|..."
   py scripts\baixar_mapillary.py --regiao itaquera --regiao jabaquara --regiao paulista --regiao se
   ```

   O padrão é 200 imagens por bairro. Os quatro bairros já têm caixas pré-definidas em volta de pontos conhecidos (estação Itaquera, estação Jabaquara, Av. Paulista e Praça da Sé); para outro bairro, use `--regiao "nome=lon_min,lat_min,lon_max,lat_max"`.
   **Se vierem fotos de carro** (comum em São Paulo, onde a maior parte do Mapillary foi gravada de carro), escolham as sequências a dedo:

   ```cmd
   py scripts\baixar_mapillary.py --regiao se --listar
   ```

   O script lista as sequências mais lentas do bairro, com um link para cada uma. Abram os links e fiquem com as que mostram a calçada do ponto de vista de quem anda. Para pegar a chave da sequência, cliquem nos três pontos (...) no canto inferior direito do visualizador e abram *Advanced*. Depois:

   ```cmd
   py scripts\baixar_mapillary.py --sequencia "se=CHAVE1" --sequencia "se=CHAVE2" --sequencia "bras=CHAVE3:teste"
   ```

   São até 25 imagens por sequência, com 8 m entre elas. O sufixo `:teste` manda a sequência inteira para o teste; sem ele, o script separa cerca de 15% sozinho.
3. **Revisar.** Abram as pastas `mapillary_sp/treino` e `mapillary_sp/teste` e apaguem as imagens que não mostram calçada (só rua, interior de ônibus, foto escura ou tremida). Contem com descartar uma parte. Se sobrar pouco, rodem o mesmo comando de novo: ele ignora as sequências já baixadas e traz imagens novas (`--por-regiao 100` = mais 100 por bairro).
4. **Créditos.** Copiem `mapillary_sp/creditos.csv` para `dados/creditos_mapillary.csv` no repositório. Linhas de imagens descartadas podem ficar: sobra crédito, não falta.
5. **Licença.** As imagens do Mapillary são CC BY-SA 4.0 e entram no dataset sem alteração (sem Resize nem aumento de dados no Roboflow), então mantêm essa licença. O projeto no Roboflow fica em CC BY 4.0, que vale para as anotações. Escrevam isso na descrição do projeto no Roboflow, no README e no PDF.

## 4. Privacidade (LGPD)

O projeto no Roboflow e o repositório são públicos, então nenhuma pessoa ou placa pode ser identificável.

- O Mapillary borra rostos e placas automaticamente, mas não é perfeito. Na revisão do passo 3, apaguem qualquer imagem com rosto ou placa legível.
- As imagens da calçada filmada ao vivo para o vídeo seguem a mesma regra: esperem o pedestre passar e não mostrem ninguém de fora do grupo com o rosto identificável.

## 5. Divisão sem vazamento

A mesma barreira aparece em várias fotos seguidas de uma sequência. Se uma cair no treino e outra no teste, o teste mede memória, não generalização.

- O script já separa **sequências inteiras** para o teste (cerca de 15%) na pasta `mapillary_sp/teste`.
- No Roboflow, subam as duas pastas em lotes separados (`sp_treino` e `sp_teste`, com a tag de mesmo nome). A divisão é escolhida quando as imagens anotadas são adicionadas ao Dataset (*Add … images to Dataset*): o lote `sp_teste` vai inteiro para **Test**; o `sp_treino` é dividido entre **Train** (cerca de 85%) e **Valid** (cerca de 15%), com **Test** em 0%.
- O teste tem só imagens de São Paulo. Imagens do dataset aberto que caírem em Test devem ir para Train.

## 6. Dataset aberto e versão final no Roboflow

Os datasets abertos de calçada quase só têm obstáculos, então entra um só: **Sidewalk obstacles** (Blindspot), com 105 imagens escolhidas a dedo e copiadas para o projeto com *Clone Images* (as anotações vêm junto).

Na hora de gerar a versão (*Versions → Generate*):

1. **Preprocessing:** só *Auto-Orient*. Sem *Resize* (as imagens do Mapillary entram sem alteração) e sem aumento de dados (o Ultralytics já faz isso no treino).
2. **Modify Classes:** reagrupe as classes do Blindspot nas nossas.

   | Classe de origem | Vira |
   | --- | --- |
   | pole, warning_column, reflective_cone, spherical_roadblock, ashcan, fire_hydrant | `obstaculo` |
   | `000000005669` (esferas de concreto), `000000005326` (cones), `000000005620` (balizadores), `000000005336` (lixeiras), `000000005967` (postes) | `obstaculo` |
   | `poste` (nome usado por engano em parte das imagens de SP) | `obstaculo` |
   | person, car, bus, truck, bicycle, motorbike, tricycle, dog, stop_sign | descartar (*Drop*) |
   | `000000002782` (carros), `000000001589` (pessoas), `000000004968` (motos), `000000002258` (bicicletas), `000000002687` (caminhão) | descartar (*Drop*) |

   As classes com nome de número são rótulos trocados no dataset original: cada uma foi identificada abrindo as imagens no Roboflow (busca `class:000000005669`). Antes de descartar uma classe de origem, confiram o que ela marca; descartar um obstáculo real deixa a barreira sem caixa.

3. Confiram em *Health Check* que sobraram só `buraco`, `desnivel` e `obstaculo` e anotem o número da versão: é o `VERSAO` do notebook.
