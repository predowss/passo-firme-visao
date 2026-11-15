# Guia de coleta e anotação — Passo Firme

Todo mundo que fotografa ou anota segue este guia. Anotação inconsistente (um anota a placa quebrada inteira, outro só a borda) derruba o mAP mais do que qualquer ajuste de treino.

## 1. Classes

| Classe | Anote | Não anote |
| --- | --- | --- |
| `buraco` | Buraco, afundamento ou pedaço faltando no piso da calçada | Tampa de bueiro fechada; junta fina entre placas; mancha ou sombra |
| `desnivel` | Degrau no meio da calçada, placa levantada, raiz erguendo o piso, borda quebrada que faz tropeçar | Rampa regular; guia (meio-fio) entre calçada e rua; degrau de entrada de imóvel fora da faixa de passagem |
| `obstaculo` | Objeto que estreita a passagem: poste, lixeira, entulho, mesa ou cadeira de comércio, placa, tapume, galho baixo | Objeto encostado no muro que não bloqueia; pessoas; animais |
| `veiculo_na_calcada` (opcional) | Carro ou moto parado em cima da calçada | Veículo na rua, mesmo encostado na guia |

A quarta classe só entra no treino com pelo menos 80 exemplos anotados.

## 2. Regras da caixa

1. **Caixa justa** em volta da barreira, sem sobra de chão limpo.
2. **Uma caixa por barreira.** Várias placas quebradas emendadas = uma caixa só; dois buracos separados por piso bom = duas caixas.
3. **Parcialmente visível:** anote se dá para ver pelo menos um terço da barreira.
4. **Longe demais:** não anote o que estiver a mais de uns 10 metros ou menor que um polegar na tela do celular. O modelo não precisa achar o que o pedestre ainda não alcança.
5. **Na dúvida entre duas classes**, use a que descreve o risco para quem anda: buraco com borda alta é `buraco`; placa levantada sem buraco é `desnivel`.
6. **Na dúvida se é barreira**, não anote e deixe a foto de fora. Foto com barreira sem anotação ensina o modelo a ignorá-la.
7. **Fotos sem barreira nenhuma** (calçada boa) entram como imagem vazia (*null*). Mantenham perto de 10% do total: ensinam o modelo a não inventar barreira.

## 3. Como fotografar

- **Quantidade:** 150 a 250 fotos próprias. Mais vale 200 fotos variadas que 400 da mesma rua.
- **Onde:** duas regiões, para comparar o desempenho depois. Uma da periferia (o distrito piloto, ex.: Itaquera ou Jabaquara) e uma do centro (ex.: entorno da Paulista).
- **Ângulo:** na altura do peito, celular na horizontal, apontando para o chão 2 a 5 metros à frente, como o vídeo de demonstração vai ver. Algumas fotos de perto e algumas de lado.
- **Variedade:** manhã, meio-dia e fim de tarde; sol e sombra; piso de concreto, ladrilho e pedra portuguesa; seco e molhado.
- **Nome do arquivo antes do upload:** `sp_<bairro>_<número>.jpg`, ex.: `sp_itaquera_001.jpg`, `sp_paulista_014.jpg`. O começo do nome é o que separa periferia e centro na avaliação.
- **Vídeos:** gravem 2 ou 3 vídeos de 30 a 60 segundos andando na calçada. Eles não entram no treino (quadros vizinhos são quase iguais e inflariam as métricas); servem para testar o tempo real e para o vídeo de entrega.

## 4. Privacidade (LGPD)

O projeto no Roboflow e o repositório são públicos, então nenhuma pessoa ou placa pode ser identificável.

- Enquadrem o chão, não as pessoas. Esperem o pedestre passar.
- Não fotografem dentro de imóveis, portões abertos ou janelas.
- Antes do upload, passem as fotos pelo anonimizador:
  `python src/anonimizar.py fotos_brutas/ fotos_anonimas/`
  e subam só a pasta `fotos_anonimas/`. Confiram uma a uma: o que escapar, apaguem.

## 5. Divisão sem vazamento

A mesma barreira fotografada de dois ângulos não pode cair uma no treino e outra no teste: o teste mediria memória, não generalização.

- Separem **por rua**: escolham 1 ou 2 ruas de cada região e reservem todas as fotos delas para o **teste**.
- Subam essas fotos num lote separado e mandem o lote inteiro para o conjunto de teste ao adicioná-lo ao dataset.
- O resto (fotos próprias e datasets abertos) é dividido pelo Roboflow em treino e validação.
