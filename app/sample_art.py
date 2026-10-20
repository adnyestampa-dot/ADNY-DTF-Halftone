"""Arte de teste nossa, para exercício do fluxo. Não vem do aplicativo original."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def criar(largura: int = 900, altura: int = 900) -> np.ndarray:
    imagem = Image.new("RGBA", (largura, altura), (0, 0, 0, 255))
    desenho = ImageDraw.Draw(imagem, "RGBA")
    for indice in range(180):
        nivel = int(255 * indice / 180)
        cor = (nivel, 40, 255 - nivel, 255)
        desenho.ellipse((80 + indice, 520 - indice // 3, 260 + indice, 700 - indice // 3), fill=cor)
    desenho.rounded_rectangle((120, 140, 780, 360), radius=28, fill=(255, 214, 10, 255))
    desenho.ellipse((560, 180, 820, 470), fill=(0, 190, 255, 255))
    desenho.ellipse((600, 220, 760, 400), fill=(0, 0, 0, 255))
    fonte = _fonte(92)
    desenho.text((150, 190), "DTF", font=fonte, fill=(20, 20, 20, 255))
    ruido = np.asarray(imagem).copy()
    rng = np.random.default_rng(7)
    for _ in range(40):
        y = int(rng.integers(40, 120))
        x = int(rng.integers(40, largura - 40))
        ruido[y, x] = (255, 255, 255, 255)
    return ruido


def gravar(caminho: str | Path) -> Path:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(criar(), "RGBA").save(destino)
    return destino


def _fonte(tamanho: int) -> ImageFont.ImageFont:
    for candidato in (
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(candidato).exists():
            return ImageFont.truetype(candidato, tamanho)
    return ImageFont.load_default()
