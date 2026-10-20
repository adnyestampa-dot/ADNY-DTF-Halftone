"""Base branca com choke de 0, 1 ou 2 px, sem ajuste escondido."""

from __future__ import annotations

import cv2
import numpy as np


def construir(tinta: np.ndarray, choke_px: int) -> np.ndarray:
    choke = int(choke_px)
    if choke not in (0, 1, 2):
        raise ValueError("A redução da base branca só aceita 0, 1 ou 2 px.")
    mascara = tinta.astype(np.uint8) * 255
    if choke:
        nucleo = np.ones((3, 3), np.uint8)
        mascara = cv2.erode(mascara, nucleo, iterations=choke)
    branco = mascara > 127
    saida = np.zeros((tinta.shape[0], tinta.shape[1], 4), dtype=np.uint8)
    saida[branco] = (255, 255, 255, 255)
    return saida
