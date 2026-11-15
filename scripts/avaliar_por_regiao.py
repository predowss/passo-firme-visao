"""Avalia o modelo separadamente por grupo de imagens (ex.: periferia x centro x datasets abertos).

Serve para o item de IA responsável: o detector funciona igual nas calçadas da
periferia e do centro? Os grupos são definidos pelo começo do nome do arquivo,
que o scripts/baixar_mapillary.py já grava como sp_<bairro>_<id>.jpg, por exemplo:
  sp_itaquera_1234.jpg, sp_jabaquara_5678.jpg, sp_paulista_9012.jpg
(o Roboflow mantém o começo do nome: sp_itaquera_1234_jpg.rf.<hash>.jpg)

Uso:
  python scripts/avaliar_por_regiao.py --modelo modelos/best.pt --dados dataset/data.yaml \
      --grupo periferia=sp_itaquera,sp_jabaquara --grupo centro=sp_paulista,sp_se

Imagens que não casam com nenhum grupo entram em "datasets abertos".
"""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import yaml

EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def ler_grupos(especificacoes: list[str]) -> dict[str, list[str]]:
    grupos = {}
    for esp in especificacoes:
        nome, _, prefixos = esp.partition("=")
        grupos[nome.strip()] = [p.strip().lower() for p in prefixos.split(",") if p.strip()]
    return grupos


def separar(imagens: list[Path], grupos: dict[str, list[str]]) -> dict[str, list[Path]]:
    separadas = {nome: [] for nome in grupos}
    separadas["datasets abertos"] = []
    for img in imagens:
        nome_arquivo = img.name.lower()
        destino = next((g for g, pref in grupos.items() if any(nome_arquivo.startswith(p) for p in pref)), None)
        separadas[destino or "datasets abertos"].append(img)
    return {g: lista for g, lista in separadas.items() if lista}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelo", required=True)
    p.add_argument("--dados", required=True, help="data.yaml do dataset")
    p.add_argument("--conjunto", default="test", choices=["val", "test"])
    p.add_argument("--grupo", action="append", default=[], help="nome=prefixo1,prefixo2 (pode repetir)")
    p.add_argument("--imgsz", type=int, default=640)
    args = p.parse_args()

    from ultralytics import YOLO

    data_yaml = Path(args.dados).resolve()
    cfg = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    base = Path(cfg.get("path") or data_yaml.parent)
    base = base if base.is_absolute() else (data_yaml.parent / base).resolve()
    pasta = Path(cfg[args.conjunto])
    pasta = pasta if pasta.is_absolute() else base / pasta
    imagens = sorted(i for i in pasta.glob("*") if i.suffix.lower() in EXTENSOES)
    grupos = separar(imagens, ler_grupos(args.grupo or ["fotos proprias=sp_"]))

    modelo = YOLO(args.modelo)
    linhas = ["| Grupo | Imagens | Precisão | Recall | mAP50 | mAP50-95 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    with tempfile.TemporaryDirectory() as tmp:
        for nome, lista in grupos.items():
            lista_txt = Path(tmp) / f"{nome.replace(' ', '_')}.txt"
            lista_txt.write_text("\n".join(str(i) for i in lista), encoding="utf-8")
            cfg_grupo = {"path": str(base), "train": str(lista_txt), "val": str(lista_txt), "names": cfg["names"]}
            yaml_grupo = Path(tmp) / f"{nome.replace(' ', '_')}.yaml"
            yaml_grupo.write_text(yaml.safe_dump(cfg_grupo, allow_unicode=True), encoding="utf-8")
            m = modelo.val(data=str(yaml_grupo), split="val", imgsz=args.imgsz, plots=False, verbose=False)
            linhas.append(
                f"| {nome} | {len(lista)} | {m.box.mp:.3f} | {m.box.mr:.3f} | {m.box.map50:.3f} | {m.box.map:.3f} |"
            )
    print("\n".join(linhas))
    print("\nGrupos com poucas imagens (menos de ~30) dão números instáveis: diga isso no PDF.")


if __name__ == "__main__":
    main()
