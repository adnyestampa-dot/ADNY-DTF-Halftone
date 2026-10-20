"""Abertura sem reamostrar. O DPI lido é o do arquivo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

DPI = 300


@dataclass(frozen=True)
class Origem:
    largura: int
    altura: int
    dpi_x: float | None
    dpi_y: float | None


def carregar(caminho: str | Path) -> tuple[np.ndarray, Origem]:
    with Image.open(caminho) as imagem:
        dpi = _ler_dpi(imagem)
        rgba = np.array(imagem.convert("RGBA"), copy=True)
    altura, largura = rgba.shape[:2]
    origem = Origem(
        largura,
        altura,
        None if dpi is None else dpi[0],
        None if dpi is None else dpi[1],
    )
    return rgba, origem


def _ler_dpi(imagem: Image.Image) -> tuple[float, float] | None:
    bruto = imagem.info.get("dpi")
    if isinstance(bruto, (int, float)):
        valor = float(bruto)
        if valor <= 0:
            return None
        return valor, valor
    if isinstance(bruto, (tuple, list)) and len(bruto) >= 2:
        eixo_x, eixo_y = float(bruto[0]), float(bruto[1])
        if eixo_x <= 0 or eixo_y <= 0:
            return None
        return eixo_x, eixo_y
    return None


def polegadas_para_px(valor: float, unidade: str, dpi: int = DPI) -> int:
    if unidade in ("in", "pol"):
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
    if unidade in ("in", "pol"):
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
