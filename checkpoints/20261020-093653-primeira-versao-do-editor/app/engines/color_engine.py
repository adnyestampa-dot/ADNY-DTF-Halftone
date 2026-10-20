"""Ajuste de matiz, saturação e luminosidade."""

from __future__ import annotations

import numpy as np

from app.model.settings import Settings


def _rgb_para_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cor = rgb.astype(np.float32) / 255.0
    vermelho, verde, azul = cor[..., 0], cor[..., 1], cor[..., 2]
    maior = np.max(cor, axis=-1)
    menor = np.min(cor, axis=-1)
    delta = maior - menor
    matiz = np.zeros_like(maior)
    tem_cor = delta > 1e-8
    seguro = np.where(tem_cor, delta, 1.0)
    matiz = np.select(
        [(maior == vermelho) & tem_cor, (maior == verde) & tem_cor, (maior == azul) & tem_cor],
        [
            ((verde - azul) / seguro) % 6.0,
            (azul - vermelho) / seguro + 2.0,
            (vermelho - verde) / seguro + 4.0,
        ],
        default=0.0,
    )
    matiz = (matiz / 6.0) % 1.0
    saturacao = np.where(maior > 1e-8, delta / np.maximum(maior, 1e-8), 0.0)
    return matiz.astype(np.float32), saturacao.astype(np.float32), maior.astype(np.float32)


def _hsv_para_rgb(matiz: np.ndarray, saturacao: np.ndarray, valor: np.ndarray) -> np.ndarray:
    faixa = matiz * 6.0
    indice = np.floor(faixa).astype(np.int32) % 6
    fracao = faixa - np.floor(faixa)
    p = valor * (1.0 - saturacao)
    q = valor * (1.0 - fracao * saturacao)
    t = valor * (1.0 - (1.0 - fracao) * saturacao)
    canal = [valor, q, p, p, t, valor]
    ordem_r = [0, 1, 2, 3, 4, 5]
    ordem_g = [4, 5, 0, 1, 2, 3]
    ordem_b = [2, 3, 4, 5, 0, 1]
    vermelho = np.select([indice == i for i in range(6)], [canal[i] for i in ordem_r])
    verde = np.select([indice == i for i in range(6)], [canal[i] for i in ordem_g])
    azul = np.select([indice == i for i in range(6)], [canal[i] for i in ordem_b])
    rgb = np.stack([vermelho, verde, azul], axis=-1)
    return np.clip(np.rint(rgb * 255.0), 0, 255).astype(np.uint8)


def aplicar(rgb: np.ndarray, ajustes: Settings) -> np.ndarray:
    if ajustes.hue == 0 and ajustes.saturation == 0 and ajustes.lightness == 0:
        return rgb.copy()
    matiz, saturacao, valor = _rgb_para_hsv(rgb)
    matiz = (matiz + np.float32(ajustes.hue) / np.float32(360.0)) % 1.0
    saturacao = np.clip(saturacao * (1.0 + np.float32(ajustes.saturation) / 100.0), 0.0, 1.0)
    valor = np.clip(valor + np.float32(ajustes.lightness) / 100.0, 0.0, 1.0)
    return _hsv_para_rgb(matiz, saturacao, valor)
