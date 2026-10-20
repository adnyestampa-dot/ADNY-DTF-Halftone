"""Levels de entrada, gamma e saída sobre a cobertura."""

from __future__ import annotations

import numpy as np

from app.model.settings import Settings


def aplicar(cobertura: np.ndarray, ajustes: Settings) -> np.ndarray:
    entrada_preto = float(ajustes.input_black)
    entrada_branco = float(ajustes.input_white)
    pixel = cobertura.astype(np.float32) * 255.0
    if entrada_branco <= entrada_preto:
        nivel = np.where(pixel >= entrada_branco, 1.0, 0.0)
    else:
        nivel = np.clip((pixel - entrada_preto) / (entrada_branco - entrada_preto), 0.0, 1.0)
    gamma = max(float(ajustes.gamma), 0.1)
    nivel = np.power(nivel, 1.0 / gamma)
    saida_preto = float(ajustes.output_black)
    saida_branco = float(ajustes.output_white)
    nivel = nivel * (saida_branco - saida_preto) + saida_preto
    return np.clip(nivel / 255.0, 0.0, 1.0).astype(np.float32)
