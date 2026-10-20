"""PNG com transparência real e alfa binário."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def separar(rgb: np.ndarray, tinta: np.ndarray) -> np.ndarray:
    saida = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
    mascara = tinta.astype(bool)
    saida[mascara, 0:3] = rgb[mascara]
    saida[mascara, 3] = 255
    return saida


def alfa_binario(rgba: np.ndarray) -> bool:
    alfa = rgba[..., 3]
    if not np.isin(alfa, (0, 255)).all():
        return False
    vazios = alfa == 0
    return not rgba[vazios, 0:3].any()


def gravar_png(
    caminho: str | Path,
    rgba: np.ndarray,
    modo_branco: str | None = None,
    dpi: tuple[float, float] | None = None,
) -> None:
    if not alfa_binario(rgba):
        raise ValueError("A exportação recusou um arquivo sem alfa binário ou com resíduo no transparente.")
    imagem = Image.fromarray(rgba, "RGBA")
    info = PngInfo()
    if modo_branco == "spot":
        info.add_text("WhiteBase", "canal branco em PNG; codificação spot original não publicada")
    _salvar_com_dpi(imagem, caminho, info, dpi)


def gravar_mascara(
    caminho: str | Path,
    rgba_branco: np.ndarray,
    dpi: tuple[float, float] | None = None,
) -> None:
    if not alfa_binario(rgba_branco):
        raise ValueError("A máscara branca não está binária.")
    _salvar_com_dpi(Image.fromarray(rgba_branco[..., 3], "L"), caminho, None, dpi)


def _salvar_com_dpi(imagem: Image.Image, caminho: str | Path, info: PngInfo | None, dpi: tuple[float, float] | None) -> None:
    extras: dict = {}
    if info is not None:
        extras["pnginfo"] = info
    if dpi is not None:
        extras["dpi"] = (float(dpi[0]), float(dpi[1]))
    imagem.save(caminho, **extras)
