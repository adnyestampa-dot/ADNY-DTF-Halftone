"""Retícula própria para DTF têxtil, restrita a 20–45 LPI."""

from __future__ import annotations

import numpy as np

from app.model.settings import SHAPES


def renderizar(
    cobertura: np.ndarray,
    lpi: float,
    angulo: float,
    forma: str,
    dpi: float = 300,
    dpi_y: float | None = None,
) -> np.ndarray:
    frequencia = float(lpi)
    if frequencia < 20 or frequencia > 45:
        raise ValueError(f"LPI {frequencia:g} recusado. A faixa do projeto é 20–45.")
    if forma not in SHAPES:
        raise ValueError(f"Forma de ponto desconhecida: {forma}")
    densidade_x = float(dpi)
    densidade_y = float(dpi if dpi_y is None else dpi_y)
    if densidade_x <= 0 or densidade_y <= 0:
        raise ValueError("O DPI do arquivo precisa ser maior que zero.")

    tom = np.clip(cobertura.astype(np.float32), 0.0, 1.0)
    altura, largura = tom.shape
    grade_y, grade_x = np.mgrid[0:altura, 0:largura].astype(np.float32)
    radianos = np.float32(np.deg2rad(float(angulo)))
    cosseno = np.cos(radianos)
    seno = np.sin(radianos)
    rotacionado_x = grade_x * cosseno + grade_y * seno
    rotacionado_y = -grade_x * seno + grade_y * cosseno
    celula_x = np.float32(densidade_x / frequencia)
    celula_y = np.float32(densidade_y / frequencia)
    local_x = np.mod(rotacionado_x, celula_x) - celula_x / 2.0
    local_y = np.mod(rotacionado_y, celula_y) - celula_y / 2.0
    meio_x = celula_x / 2.0
    meio_y = celula_y / 2.0

    if forma == "circle":
        distancia = np.hypot(local_x / meio_x, local_y / meio_y)
        limite = 2.0 * np.sqrt(np.clip(tom, 0.0, 1.0) / np.float32(np.pi))
    elif forma == "ellipse":
        distancia = np.hypot(local_x / (meio_x * np.float32(1.15)), local_y / (meio_y * np.float32(0.72)))
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    elif forma == "diamond":
        distancia = np.abs(local_x) / meio_x + np.abs(local_y) / meio_y
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    elif forma == "square":
        distancia = np.maximum(np.abs(local_x) / meio_x, np.abs(local_y) / meio_y)
        limite = np.sqrt(np.clip(tom, 0.0, 1.0))
    else:
        distancia = np.abs(local_x) / meio_x
        limite = np.clip(tom, 0.0, 1.0)

    tinta = distancia <= limite
    tinta = np.where(tom >= np.float32(0.999), True, tinta)
    tinta = np.where(tom <= np.float32(0.0), False, tinta)
    return tinta.astype(bool)
