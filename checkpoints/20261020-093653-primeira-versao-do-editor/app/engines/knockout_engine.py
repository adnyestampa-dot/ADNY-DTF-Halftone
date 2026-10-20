"""Remove a cor de knockout e gera a cobertura que alimenta a retícula."""

from __future__ import annotations

import numpy as np

DISTANCIA_MAXIMA = np.float32(441.67296)


def cobertura(
    rgb: np.ndarray,
    knockout: tuple[int, int, int],
    limite: int,
    alfa: np.ndarray,
) -> np.ndarray:
    referencia = np.array(knockout, dtype=np.float32)
    diferenca = rgb.astype(np.float32) - referencia
    distancia = np.sqrt(np.sum(diferenca * diferenca, axis=-1))
    nivel = distancia / DISTANCIA_MAXIMA
    nivel = np.where(distancia <= np.float32(limite), 0.0, nivel)
    return np.clip(nivel * alfa.astype(np.float32), 0.0, 1.0).astype(np.float32)
