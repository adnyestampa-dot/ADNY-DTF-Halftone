"""Motor central. Encadeia os motores especializados sem fundir os algoritmos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.engines import (
    cleanup_engine,
    color_engine,
    export_engine,
    halftone_engine,
    knockout_engine,
    levels_engine,
    underbase_engine,
)
from app.model.settings import Settings


@dataclass
class Resultado:
    separacao: np.ndarray
    base_branca: np.ndarray | None
    tinta: np.ndarray
    lpi: float
    celula_px: float


class MotorCentral:
    def processar(
        self,
        rgba: np.ndarray,
        ajustes: Settings,
        restaurar: np.ndarray | None = None,
        remover: np.ndarray | None = None,
    ) -> Resultado:
        imagem = np.asarray(rgba)
        if imagem.ndim != 3 or imagem.shape[2] != 4:
            raise ValueError("O motor central recebe RGBA.")
        ajustes.validate()
        rgb = color_engine.aplicar(imagem[..., 0:3], ajustes)
        alfa = imagem[..., 3].astype(np.float32) / 255.0
        cobertura = knockout_engine.cobertura(rgb, ajustes.knockout, int(ajustes.mask_threshold), alfa)
        cobertura = levels_engine.aplicar(cobertura, ajustes)

        if ajustes.halftone_enabled:
            tinta = halftone_engine.renderizar(
                cobertura,
                float(ajustes.lpi),
                float(ajustes.angle),
                ajustes.dot_shape,
                int(ajustes.dpi),
            )
        else:
            tinta = cobertura >= np.float32(0.5)

        tinta = cleanup_engine.aplicar(tinta, int(ajustes.cleanup))
        if restaurar is not None:
            solido = restaurar.astype(bool) & (imagem[..., 3] >= 128)
            tinta = np.where(solido, True, tinta)
            tinta = np.where(restaurar.astype(bool) & ~solido, False, tinta)
        if remover is not None:
            tinta = np.where(remover.astype(bool), False, tinta)

        cor_final = rgb
        if restaurar is not None and np.any(restaurar):
            cor_final = rgb.copy()
            cor_final[restaurar.astype(bool)] = imagem[..., 0:3][restaurar.astype(bool)]

        separacao = export_engine.separar(cor_final, tinta)
        base = underbase_engine.construir(tinta, int(ajustes.choke_px)) if ajustes.underbase else None
        if not export_engine.alfa_binario(separacao):
            raise ValueError("A separação saiu sem alfa binário.")
        if base is not None and not export_engine.alfa_binario(base):
            raise ValueError("A base branca saiu sem alfa binário.")
        return Resultado(
            separacao=separacao,
            base_branca=base,
            tinta=tinta.astype(bool),
            lpi=float(ajustes.lpi),
            celula_px=float(ajustes.dpi) / float(ajustes.lpi),
        )
