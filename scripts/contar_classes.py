"""Conta imagens e anotações por classe em cada conjunto (treino, validação, teste).

Gera a tabela do dataset que vai no PDF e no README.

Uso:
  python scripts/contar_classes.py caminho/para/data.yaml
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import yaml

EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def pasta_de_rotulos(pasta_imagens: Path) -> Path:
    """No formato YOLO, .../images vira .../labels (mesma estrutura)."""
    partes = list(pasta_imagens.parts)
    for i in range(len(partes) - 1, -1, -1):
        if partes[i] == "images":
            partes[i] = "labels"
            return Path(*partes)
    return pasta_imagens.parent / "labels"


def contar(data_yaml: str | Path) -> tuple[list[str], dict]:
    data_yaml = Path(data_yaml)
    cfg = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    nomes = cfg["names"]
    nomes = [nomes[k] for k in sorted(nomes)] if isinstance(nomes, dict) else list(nomes)
    base = Path(cfg.get("path") or data_yaml.parent)
    if not base.is_absolute():
        base = (data_yaml.parent / base).resolve()

    resultado = {}
    for conjunto in ("train", "val", "test"):
        if not cfg.get(conjunto):
            continue
        pasta_img = Path(cfg[conjunto])
        pasta_img = pasta_img if pasta_img.is_absolute() else (base / pasta_img)
        imagens = [p for p in pasta_img.glob("*") if p.suffix.lower() in EXTENSOES]
        pasta_lbl = pasta_de_rotulos(pasta_img)
        por_classe: Counter = Counter()
        sem_anotacao = 0
        for img in imagens:
            rotulo = pasta_lbl / (img.stem + ".txt")
            linhas = [l for l in rotulo.read_text().splitlines() if l.strip()] if rotulo.exists() else []
            if not linhas:
                sem_anotacao += 1
            for linha in linhas:
                por_classe[int(float(linha.split()[0]))] += 1
        resultado[conjunto] = {"imagens": len(imagens), "sem_anotacao": sem_anotacao, "por_classe": por_classe}
    return nomes, resultado


def tabela_markdown(nomes: list[str], resultado: dict) -> str:
    conjuntos = list(resultado)
    cab = "| Classe | " + " | ".join(conjuntos) + " | Total |"
    sep = "| --- | " + " | ".join("---:" for _ in conjuntos) + " | ---: |"
    linhas = [cab, sep]
    for i, nome in enumerate(nomes):
        valores = [resultado[c]["por_classe"].get(i, 0) for c in conjuntos]
        linhas.append(f"| {nome} | " + " | ".join(map(str, valores)) + f" | {sum(valores)} |")
    imgs = [resultado[c]["imagens"] for c in conjuntos]
    nulas = [resultado[c]["sem_anotacao"] for c in conjuntos]
    linhas.append("| **imagens** | " + " | ".join(map(str, imgs)) + f" | {sum(imgs)} |")
    linhas.append("| imagens sem barreira | " + " | ".join(map(str, nulas)) + f" | {sum(nulas)} |")
    return "\n".join(linhas)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    nomes, resultado = contar(sys.argv[1])
    print(tabela_markdown(nomes, resultado))
