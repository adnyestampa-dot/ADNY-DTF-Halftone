"""Cópia restaurável do projeto, independente do autor do Git."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / "checkpoints"
IGNORAR = {"checkpoints", "__pycache__", ".git", ".pytest_cache"}


def criar(etapa: str) -> Path:
    carimbo = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    pasta = DESTINO / f"{carimbo}-{_slug(etapa)}"
    pasta.mkdir(parents=True, exist_ok=False)

    def _ignorar(diretorio: str, nomes: list[str]) -> set[str]:
        return {nome for nome in nomes if nome in IGNORAR or nome.endswith(".pyc")}

    for item in ROOT.iterdir():
        if item.name in IGNORAR:
            continue
        alvo = pasta / item.name
        if item.is_dir():
            shutil.copytree(item, alvo, ignore=_ignorar)
        else:
            shutil.copy2(item, alvo)
    (pasta / "ETAPA.txt").write_text(etapa, encoding="utf-8")
    return pasta


def _slug(texto: str) -> str:
    limpo = "".join(caractere if caractere.isalnum() else "-" for caractere in texto.lower())
    while "--" in limpo:
        limpo = limpo.replace("--", "-")
    return limpo.strip("-") or "checkpoint"
