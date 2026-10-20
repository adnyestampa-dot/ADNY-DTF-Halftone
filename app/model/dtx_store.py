"""Leitura e gravação do projeto .dtx do DTF HALFTONE ADNY.

O pacote guarda a imagem e os ajustes. Não é o formato proprietário do aplicativo original.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from app import NOME
from app.model.settings import Settings


def salvar(caminho: str | Path, rgba: np.ndarray, ajustes: Settings, restaurar: np.ndarray | None, remover: np.ndarray | None) -> None:
    ajustes.validate()
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    manifesto = {
        "format": "dtx-clone-1",
        "compatible_with_original": False,
        "note": f"Arquivo do {NOME}. O .dtx original não teve o formato publicado.",
    }
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED) as pacote:
        pacote.writestr("manifest.json", json.dumps(manifesto, ensure_ascii=False, indent=2))
        pacote.writestr("settings.json", json.dumps(ajustes.to_dict(), ensure_ascii=False, indent=2))
        pacote.writestr("image.png", _png(rgba, "RGBA"))
        if restaurar is not None and np.any(restaurar):
            pacote.writestr("restore.png", _png(restaurar.astype(np.uint8) * 255, "L"))
        if remover is not None and np.any(remover):
            pacote.writestr("remove.png", _png(remover.astype(np.uint8) * 255, "L"))


def carregar(caminho: str | Path) -> tuple[np.ndarray, Settings, np.ndarray | None, np.ndarray | None]:
    with zipfile.ZipFile(caminho, "r") as pacote:
        nomes = set(pacote.namelist())
        if "manifest.json" not in nomes or "image.png" not in nomes or "settings.json" not in nomes:
            raise ValueError(f"Este arquivo não é um projeto do {NOME}.")
        manifesto = json.loads(pacote.read("manifest.json"))
        if manifesto.get("format") != "dtx-clone-1":
            raise ValueError(f"O {NOME} não reconhece o formato deste .dtx.")
        rgba = np.asarray(Image.open(io.BytesIO(pacote.read("image.png"))).convert("RGBA"))
        ajustes = Settings.from_dict(json.loads(pacote.read("settings.json")))
        restaurar = _mascara(pacote, "restore.png", rgba.shape[:2]) if "restore.png" in nomes else None
        remover = _mascara(pacote, "remove.png", rgba.shape[:2]) if "remove.png" in nomes else None
    return rgba, ajustes, restaurar, remover


def _png(arr: np.ndarray, modo: str) -> bytes:
    buffer = io.BytesIO()
    Image.fromarray(arr, modo).save(buffer, format="PNG")
    return buffer.getvalue()


def _mascara(pacote: zipfile.ZipFile, nome: str, forma: tuple[int, int]) -> np.ndarray:
    imagem = np.asarray(Image.open(io.BytesIO(pacote.read(nome))).convert("L"))
    if imagem.shape != forma:
        raise ValueError("A máscara do projeto não combina com a imagem.")
    return imagem >= 128
