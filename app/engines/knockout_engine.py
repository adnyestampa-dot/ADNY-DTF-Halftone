"""Presença da arte. O tom fica no motor de tom.

Pixel cuja cor está até o limiar visível da cor de knockout é camiseta.
"""

from __future__ import annotations

import numpy as np


def presente(rgb: np.ndarray, knockout: tuple[int, int, int], limite: int) -> np.ndarray:
    referencia = np.array(knockout, dtype=np.float32)
    diferenca = rgb.astype(np.float32) - referencia
    distancia = np.sqrt(np.sum(diferenca * diferenca, axis=-1))
    return distancia > np.float32(limite)
