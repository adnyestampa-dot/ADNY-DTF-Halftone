"""Retícula própria para DTF têxtil, restrita a 20–45 LPI."""

from __future__ import annotations

import numpy as np

from app.model.settings import SHAPES


def renderizar(
    cobertura: np.ndarray,
    lpi: float,
    angulo: float,
    forma: str,
    dpi: int = 300,
) -> np.ndarray:
    frequencia = float(lpi)
    if frequencia < 20 or frequencia > 45:
        raise ValueError(f"LPI {frequencia:g} recusado. A faixa do projeto é 20–45.")
    if forma not in SHAPES:
        raise ValueError(f"Forma de ponto desconhecida: {forma}")
    if int(dpi) != 300:
        raise ValueError("A retícula deste projeto é calculada a 300 DPI.")

    tom = np.clip(cobertura.astype(np.float32), 0.0, 1.0)
    altura, largura = tom.shape
    grade_y, grade_x = np.mgrid[0:altura, 0:largura].astype(np.float32)
    radianos = np.float32(np.deg2rad(float(angulo)))
    cosseno = np.cos(radianos)
    seno = np.sin(radianos)
    rotacionado_x = grade_x * cosseno + grade_y * seno
    rotacionado_y = -grade_x * seno + grade_y * cosseno
    celula = np.float32(dpi / frequencia)
    local_x = np.mod(rotacionado_x, celula) - celula / 2.0
    local_y = np.mod(rotacionado_y, celula) - celula / 2.0
    meio = celula / 2.0

    if forma == "circle":
        distancia = np.hypot(local_x, local_y) / meio
        limite = 2.0 * np.sqrt(np.clip(tom, 0.0, 1.0) / np.float32(np.pi))
    elif forma == "ellipse":
        distancia = np.hypot(local_x / (meio * np.float32(1.15)), local_y / (meio * np.float32(0.72)))
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    elif forma == "diamond":
        distancia = (np.abs(local_x) + np.abs(local_y)) / meio
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    elif forma == "square":
        distancia = np.maximum(np.abs(local_x), np.abs(local_y)) / meio
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    else:
        distancia = np.abs(local_x) / meio
        limite = np.clip(tom, 0.0, 1.0)

    tinta = distancia <= limite
    tinta = np.where(tom >= np.float32(0.999), True, tinta)
    tinta = np.where(tom <= np.float32(0.0), False, tinta)
    return tinta.astype(bool)
