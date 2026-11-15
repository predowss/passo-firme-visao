"""Baixa imagens de calçadas de São Paulo do Mapillary, por bairro, para o treino do Passo Firme.

O que o script faz:
  1. Busca as imagens de cada bairro na API do Mapillary, em blocos pequenos
     (a API recusa caixas grandes e às vezes estoura o tempo em áreas densas).
  2. Agrupa por sequência e calcula a velocidade de quem capturou: fica só com
     sequências feitas A PÉ (mediana de 0,5 a 2,2 m/s e pico até 3,5 m/s), que têm
     o ponto de vista do pedestre. O pico barra carros parados no trânsito.
  3. Pega poucas imagens por sequência, espaçadas, para evitar fotos quase iguais.
  4. Separa sequências inteiras para o TESTE (nenhuma sequência aparece em treino e teste).
  5. Baixa as imagens como  sp_<bairro>_<id>.jpg  e grava  creditos.csv  com autor,
     link e licença de cada uma (as imagens do Mapillary são CC BY-SA 4.0).

Token: crie uma conta em mapillary.com, registre um app em Developers e copie o
"Client Token" (começa com MLY|). No Prompt de Comando do Windows, use ASPAS,
porque o caractere | tem significado especial:
  set "MAPILLARY_TOKEN=MLY|1234|abcd"

Exemplos:
  # bairros pré-definidos (confiram as caixas no mapa antes)
  py scripts\\baixar_mapillary.py --regiao itaquera --regiao jabaquara --regiao paulista --regiao se

  # bairro com caixa própria: nome=lon_min,lat_min,lon_max,lat_max
  py scripts\\baixar_mapillary.py --regiao "penha=-46.555,-23.535,-46.530,-23.515" --por-regiao 150
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

API = "https://graph.mapillary.com/images"
CAMPOS_COMPLETOS = "id,thumb_2048_url,captured_at,sequence,geometry,camera_type,creator"
CAMPOS_BASICOS = "id,thumb_2048_url,captured_at,sequence,geometry"
LICENCA = "CC BY-SA 4.0"
AREA_MAXIMA = 0.01   # graus quadrados aceitos pela API em uma caixa
LIMITE_POR_PEDIDO = 2000

# centro aproximado (lat, lon) de cada bairro; a caixa vai ±0,012° (~2,6 km de lado)
PRESETS = {
    "itaquera": (-23.542, -46.471),
    "jabaquara": (-23.646, -46.641),
    "paulista": (-23.5614, -46.6559),
    "se": (-23.5505, -46.6333),
}
MEIA_CAIXA = 0.012


class CampoInvalido(Exception):
    """A API recusou algum campo pedido (ex.: creator)."""


# ----------------------------------------------------------------------------- geometria

def caixa_da_regiao(especificacao: str) -> tuple[str, tuple[float, float, float, float]]:
    """'itaquera' (pré-definido) ou 'nome=lon_min,lat_min,lon_max,lat_max'."""
    nome, sep, coords = especificacao.partition("=")
    nome = nome.strip().lower().replace(" ", "_")
    if sep:
        lon_min, lat_min, lon_max, lat_max = (float(v) for v in coords.split(","))
    elif nome in PRESETS:
        lat, lon = PRESETS[nome]
        lon_min, lat_min, lon_max, lat_max = lon - MEIA_CAIXA, lat - MEIA_CAIXA, lon + MEIA_CAIXA, lat + MEIA_CAIXA
    else:
        raise SystemExit(f"Região '{nome}' não é pré-definida. Use nome=lon_min,lat_min,lon_max,lat_max.")
    if lon_min >= lon_max or lat_min >= lat_max:
        raise SystemExit(f"Caixa inválida para '{nome}': confira a ordem lon_min,lat_min,lon_max,lat_max.")
    area = (lon_max - lon_min) * (lat_max - lat_min)
    if area >= AREA_MAXIMA:
        raise SystemExit(f"A caixa de '{nome}' tem {area:.4f} graus²; a API aceita menos de {AREA_MAXIMA}.")
    return nome, (lon_min, lat_min, lon_max, lat_max)


def dividir(caixa: tuple[float, float, float, float], passo: float) -> list[tuple[float, float, float, float]]:
    """Corta a caixa em blocos de no máximo passo × passo graus."""
    lon_min, lat_min, lon_max, lat_max = caixa
    blocos = []
    lat = lat_min
    while lat < lat_max - 1e-12:
        lon = lon_min
        lat_fim = min(lat + passo, lat_max)
        while lon < lon_max - 1e-12:
            lon_fim = min(lon + passo, lon_max)
            blocos.append((lon, lat, lon_fim, lat_fim))
            lon = lon_fim
        lat = lat_fim
    return blocos


def distancia_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distância em metros entre dois pontos (lon, lat)."""
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def instante_ms(valor) -> int | None:
    """captured_at pode vir em milissegundos (número) ou como texto ISO."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return int(valor)
    try:
        return int(datetime.fromisoformat(str(valor).replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError:
        return None


# ----------------------------------------------------------------------------- seleção

def perfil_velocidade(imagens: list[dict]) -> tuple[float, float, float] | None:
    """(mediana, pico, fração parada) da velocidade de uma sequência, em m/s.

    pico = percentil 90; fração parada = trechos abaixo de 0,3 m/s.
    Só a mediana não basta: um carro no trânsito tem mediana de pedestre, mas ou
    arranca em algum momento (o pico denuncia) ou passa muito tempo parado (a
    fração parada denuncia). Precisa de pelo menos 3 trechos.
    """
    pontos = sorted((i for i in imagens if i.get("_t") is not None and i.get("_pos")), key=lambda i: i["_t"])
    velocidades = []
    for a, b in zip(pontos, pontos[1:]):
        dt = (b["_t"] - a["_t"]) / 1000
        if 0 < dt <= 30:  # ignora pausas longas entre capturas
            velocidades.append(distancia_m(a["_pos"], b["_pos"]) / dt)
    if len(velocidades) < 3:
        return None
    parado = sum(v < 0.3 for v in velocidades) / len(velocidades)
    velocidades.sort()
    mediana = velocidades[len(velocidades) // 2]
    pico = velocidades[min(len(velocidades) - 1, int(0.9 * len(velocidades)))]
    return mediana, pico, parado


def velocidade_mediana(imagens: list[dict]) -> float | None:
    perfil = perfil_velocidade(imagens)
    return perfil[0] if perfil else None


def espacar(imagens: list[dict], distancia_minima: float, maximo: int) -> list[dict]:
    """Escolhe imagens da sequência com pelo menos distancia_minima metros entre si."""
    escolhidas: list[dict] = []
    for img in sorted(imagens, key=lambda i: i.get("_t") or 0):
        if all(distancia_m(img["_pos"], e["_pos"]) >= distancia_minima for e in escolhidas):
            escolhidas.append(img)
            if len(escolhidas) >= maximo:
                break
    return escolhidas


def selecionar(
    imagens: list[dict],
    quantidade: int,
    fracao_teste: float,
    vel_min: float,
    vel_max: float,
    vel_pico: float,
    max_parado: float,
    qualquer_velocidade: bool,
    distancia_minima: float,
    max_por_sequencia: int,
    semente: int,
) -> tuple[list[dict], dict]:
    """Devolve as imagens escolhidas (com '_conjunto' = treino/teste) e um resumo da filtragem."""
    por_sequencia: dict[str, list[dict]] = defaultdict(list)
    for img in imagens:
        por_sequencia[img.get("sequence") or f"sem-seq-{img['id']}"].append(img)

    resumo = {"sequencias": len(por_sequencia), "a_pe": 0, "outras": 0, "sem_velocidade": 0}
    candidatas = []
    for seq, lista in por_sequencia.items():
        perfil = perfil_velocidade(lista)
        if perfil is None:
            resumo["sem_velocidade"] += 1
            if not qualquer_velocidade:
                continue
        elif vel_min <= perfil[0] <= vel_max and perfil[1] <= vel_pico and perfil[2] <= max_parado:
            resumo["a_pe"] += 1
        else:
            resumo["outras"] += 1
            if not qualquer_velocidade:
                continue
        amostra = espacar(lista, distancia_minima, max_por_sequencia)
        if amostra:
            candidatas.append((seq, amostra))

    rnd = random.Random(semente)
    rnd.shuffle(candidatas)
    escolhidas: list[dict] = []
    for seq, amostra in candidatas:
        if len(escolhidas) >= quantidade:
            break
        escolhidas.extend(amostra[: quantidade - len(escolhidas)])

    # sequências inteiras vão para o teste até cobrir a fração pedida, sem passar muito dela
    tamanhos: dict = {}
    for img in escolhidas:
        tamanhos[img.get("sequence")] = tamanhos.get(img.get("sequence"), 0) + 1
    meta_teste = max(1, round(len(escolhidas) * fracao_teste))
    no_teste: set = set()
    contagem = 0
    if len(tamanhos) > 1:
        for seq, n in tamanhos.items():
            if contagem >= meta_teste:
                break
            if contagem + n <= meta_teste * 1.5:
                no_teste.add(seq)
                contagem += n
        if not no_teste:  # todas as sequências são grandes: vai a menor
            no_teste.add(min(tamanhos, key=tamanhos.get))
    for img in escolhidas:
        img["_conjunto"] = "teste" if img.get("sequence") in no_teste else "treino"
    return escolhidas, resumo


# ----------------------------------------------------------------------------- API

def buscar_bloco(sessao, token: str, caixa, campos: str, profundidade: int = 0) -> list[dict]:
    """Busca as imagens de um bloco; divide o bloco se a API estourar o tempo ou bater o limite."""
    params = {
        "access_token": token,
        "fields": campos,
        "bbox": ",".join(f"{v:.6f}" for v in caixa),
        "limit": LIMITE_POR_PEDIDO,
        "is_pano": "false",
    }
    ultimo_erro = ""
    for tentativa in range(3):
        try:
            r = sessao.get(API, params=params, timeout=60)
        except Exception as e:  # rede instável: tenta de novo
            ultimo_erro = str(e)
            time.sleep(2 * (tentativa + 1))
            continue
        if r.status_code == 200:
            dados = r.json().get("data", [])
            if len(dados) >= LIMITE_POR_PEDIDO and profundidade < 3:
                return _subdividir(sessao, token, caixa, campos, profundidade)
            return dados
        if r.status_code in (401, 403):
            raise SystemExit("Token recusado pela API do Mapillary. Confira o MAPILLARY_TOKEN (Client Token, começa com MLY|).")
        if r.status_code == 400 and "field" in r.text.lower():
            raise CampoInvalido(r.text[:300])
        ultimo_erro = f"HTTP {r.status_code}: {r.text[:200]}"
        if r.status_code >= 500 and profundidade < 3:
            return _subdividir(sessao, token, caixa, campos, profundidade)
        time.sleep(2 * (tentativa + 1))
    print(f"  aviso: bloco ignorado após 3 tentativas ({ultimo_erro})")
    return []


def _subdividir(sessao, token, caixa, campos, profundidade):
    lon_min, lat_min, lon_max, lat_max = caixa
    passo = max(lon_max - lon_min, lat_max - lat_min) / 2
    resultado = []
    for bloco in dividir(caixa, passo):
        resultado.extend(buscar_bloco(sessao, token, bloco, campos, profundidade + 1))
    return resultado


def preparar(dados: list[dict], ano_minimo: int) -> list[dict]:
    """Normaliza os registros da API e descarta panorâmicas, fisheye, sem URL e antigas demais."""
    vistos, imagens = set(), []
    for d in dados:
        if d.get("id") in vistos or not d.get("thumb_2048_url"):
            continue
        tipo = (d.get("camera_type") or "perspective").lower()
        if tipo not in ("perspective", "brown"):
            continue
        coords = (d.get("geometry") or {}).get("coordinates")
        if not coords:
            continue
        t = instante_ms(d.get("captured_at"))
        if t is not None and datetime.fromtimestamp(t / 1000, tz=timezone.utc).year < ano_minimo:
            continue
        vistos.add(d["id"])
        imagens.append({**d, "_pos": (float(coords[0]), float(coords[1])), "_t": t})
    return imagens


def autor(img: dict) -> str:
    criador = img.get("creator")
    if isinstance(criador, dict):
        return criador.get("username") or criador.get("id") or ""
    return ""


# ----------------------------------------------------------------------------- principal

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--regiao", action="append", required=True, help="bairro pré-definido ou nome=lon_min,lat_min,lon_max,lat_max")
    p.add_argument("--por-regiao", type=int, default=200, help="imagens NOVAS por bairro nesta rodada (padrão 200)")
    p.add_argument("--fracao-teste", type=float, default=0.15, help="fração reservada ao teste, por sequência")
    p.add_argument("--saida", default="mapillary_sp", help="pasta de saída")
    p.add_argument("--token", default=os.getenv("MAPILLARY_TOKEN", ""), help="Client Token (ou variável MAPILLARY_TOKEN)")
    p.add_argument("--vel-min", type=float, default=0.5, help="velocidade mediana mínima de quem captura (m/s)")
    p.add_argument("--vel-max", type=float, default=2.2, help="velocidade mediana máxima de quem anda a pé (m/s)")
    p.add_argument("--vel-pico", type=float, default=3.5, help="pico (percentil 90) máximo; acima disso é veículo (m/s)")
    p.add_argument("--max-parado", type=float, default=0.3, help="fração máxima de trechos parados (carro no trânsito)")
    p.add_argument("--qualquer-velocidade", action="store_true", help="aceita sequências de carro e bicicleta também")
    p.add_argument("--distancia-minima", type=float, default=8.0, help="metros entre imagens da mesma sequência")
    p.add_argument("--max-por-sequencia", type=int, default=8, help="máximo de imagens por sequência (mais variedade)")
    p.add_argument("--desde", type=int, default=2018, help="ano mínimo de captura")
    p.add_argument("--semente", type=int, default=42)
    args = p.parse_args()

    if not args.token:
        raise SystemExit('Falta o token. No cmd:  set "MAPILLARY_TOKEN=MLY|..."  (com aspas) e rode de novo.')
    import requests

    regioes = [caixa_da_regiao(r) for r in args.regiao]
    saida = Path(args.saida)
    for conjunto in ("treino", "teste"):
        (saida / conjunto).mkdir(parents=True, exist_ok=True)
    caminho_creditos = saida / "creditos.csv"
    novo_arquivo = not caminho_creditos.exists()
    # sequências de rodadas anteriores ficam de fora: rodar de novo só traz imagens novas,
    # e nenhuma sequência se divide entre treino e teste
    sequencias_usadas: set[str] = set()
    if not novo_arquivo:
        with caminho_creditos.open(encoding="utf-8") as f:
            sequencias_usadas = {linha["sequencia"] for linha in csv.DictReader(f) if linha.get("sequencia")}
        print(f"{len(sequencias_usadas)} sequências já baixadas antes serão ignoradas.")

    sessao = requests.Session()
    campos = CAMPOS_COMPLETOS
    with caminho_creditos.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if novo_arquivo:
            escritor.writerow(["arquivo", "conjunto", "regiao", "image_id", "sequencia", "autor",
                               "capturada_em", "link", "licenca"])
        for nome, caixa in regioes:
            print(f"\n== {nome}: buscando imagens em {caixa}")
            dados = []
            for bloco in dividir(caixa, 0.006):
                try:
                    dados.extend(buscar_bloco(sessao, args.token, bloco, campos))
                except CampoInvalido:
                    print("  a API recusou campos extras; seguindo só com os campos básicos")
                    campos = CAMPOS_BASICOS
                    dados.extend(buscar_bloco(sessao, args.token, bloco, campos))
            imagens = [i for i in preparar(dados, args.desde) if i.get("sequence") not in sequencias_usadas]
            escolhidas, resumo = selecionar(
                imagens, args.por_regiao, args.fracao_teste, args.vel_min, args.vel_max, args.vel_pico,
                args.max_parado, args.qualquer_velocidade, args.distancia_minima, args.max_por_sequencia, args.semente,
            )
            print(f"  {len(imagens)} imagens válidas em {resumo['sequencias']} sequências "
                  f"({resumo['a_pe']} a pé, {resumo['outras']} de veículo, {resumo['sem_velocidade']} sem dado de velocidade)")
            if len(escolhidas) < args.por_regiao:
                print(f"  aviso: só {len(escolhidas)} imagens a pé disponíveis. Para mais, aumente a caixa "
                      "ou use --qualquer-velocidade.")

            baixadas = 0
            for img in escolhidas:
                arquivo = f"sp_{nome}_{img['id']}.jpg"
                destino = saida / img["_conjunto"] / arquivo
                if not destino.exists():
                    try:
                        r = sessao.get(img["thumb_2048_url"], timeout=60)
                        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
                            print(f"  pulei {img['id']} (HTTP {r.status_code})")
                            continue
                        destino.write_bytes(r.content)
                    except Exception as e:
                        print(f"  pulei {img['id']} ({e})")
                        continue
                    time.sleep(0.05)
                baixadas += 1
                t = img.get("_t")
                data = datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%d") if t else ""
                escritor.writerow([arquivo, img["_conjunto"], nome, img["id"], img.get("sequence", ""), autor(img),
                                   data, f"https://www.mapillary.com/app/?pKey={img['id']}", LICENCA])
            teste = sum(1 for i in escolhidas if i["_conjunto"] == "teste")
            print(f"  {baixadas} imagens salvas ({teste} reservadas ao teste)")

    print(f"\nPronto. Imagens em {saida}/treino e {saida}/teste; créditos em {caminho_creditos}.")
    print("Antes de subir no Roboflow, olhem as imagens e apaguem as que não mostram calçada.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
