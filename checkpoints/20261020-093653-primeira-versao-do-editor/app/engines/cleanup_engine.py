"""Remove ilhas de tinta menores que o valor exibido no Cleanup."""

from __future__ import annotations

import cv2
import numpy as np


def aplicar(tinta: np.ndarray, intensidade: int) -> np.ndarray:
    minimo = int(intensidade)
    if minimo <= 0:
        return tinta.astype(bool)
    mascara = tinta.astype(np.uint8)
    _quantidade, rotulos, estatisticas, _centros = cv2.connectedComponentsWithStats(mascara, connectivity=8)
    areas = estatisticas[:, cv2.CC_STAT_AREA]
    manter = areas >= minimo
    manter[0] = False
    return manter[rotulos]
