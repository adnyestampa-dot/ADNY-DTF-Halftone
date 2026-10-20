"""Abertura, escala a 300 DPI e recorte."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

DPI = 300


def carregar(caminho: str | Path) -> np.ndarray:
    imagem = Image.open(caminho).convert("RGBA")
    return np.asarray(imagem)


def polegadas_para_px(valor: float, unidade: str, dpi: int = DPI) -> int:
    if unidade == "in":
        polegadas = float(valor)
    elif unidade == "cm":
        polegadas = float(valor) / 2.54
    elif unidade == "mm":
        polegadas = float(valor) / 25.4
    else:
        raise ValueError(f"Unidade desconhecida: {unidade}")
    return max(1, int(round(polegadas * dpi)))


def px_para_unidade(px: int, unidade: str, dpi: int = DPI) -> float:
    polegadas = px / dpi
    if unidade == "in":
        return polegadas
    if unidade == "cm":
        return polegadas * 2.54
    if unidade == "mm":
        return polegadas * 25.4
    raise ValueError(f"Unidade desconhecida: {unidade}")


def redimensionar(rgba: np.ndarray, largura: int, altura: int) -> np.ndarray:
    imagem = Image.fromarray(rgba, "RGBA")
    imagem = imagem.resize((max(1, largura), max(1, altura)), Image.Resampling.LANCZOS)
    return np.asarray(imagem)


def recortar(rgba: np.ndarray, x: int, y: int, largura: int, altura: int) -> np.ndarray:
    altura_img, largura_img = rgba.shape[:2]
    x0 = min(max(0, int(x)), largura_img - 1)
    y0 = min(max(0, int(y)), altura_img - 1)
    x1 = min(largura_img, x0 + max(1, int(largura)))
    y1 = min(altura_img, y0 + max(1, int(altura)))
    return rgba[y0:y1, x0:x1].copy()
