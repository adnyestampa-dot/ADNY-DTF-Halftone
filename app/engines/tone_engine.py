"""Tom da estampa. A presença fica no knockout; aqui se decide chapado ou ponto.

A regra vem da pesquisa pública de DTF, não do aplicativo de referência.
Cor opaca e viva permanece contínua. Alfa parcial acompanha a opacidade.
Cinza opaco em rampa vira ponto. O diâmetro RGB só entra nesse cinza.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.engines.knockout_engine import presente

DIAMETRO_RGB = np.float32(np.sqrt(3.0) * 255.0)
SATURACAO_NEUTRA = np.float32(0.15)
JANELA = 31


def cobertura(
    rgb: np.ndarray,
    knockout: tuple[int, int, int],
    limite: int,
    alfa: np.ndarray,
) -> np.ndarray:
    cor = rgb.astype(np.float32)
    alfa_n = np.clip(alfa.astype(np.float32), 0.0, 1.0)
    na_arte = presente(cor, knockout, limite) & (alfa_n > 0.0)
    opaco = alfa_n >= np.float32(0.999)

    maior = np.max(cor, axis=-1)
    menor = np.min(cor, axis=-1)
    saturacao = np.where(maior > 0.0, (maior - menor) / np.maximum(maior, 1.0), 0.0)
    neutro = saturacao <= SATURACAO_NEUTRA
    luma = (0.2126 * cor[..., 0] + 0.7152 * cor[..., 1] + 0.0722 * cor[..., 2]) / np.float32(255.0)
    rampa = _rampa_neutra(luma)

    distancia = _distancia(cor, knockout)
    tom_cinza = np.clip(distancia / DIAMETRO_RGB, 0.0, 1.0)

    nivel = np.where(opaco, np.float32(1.0), alfa_n)
    nivel = np.where(opaco & neutro & rampa, tom_cinza, nivel)
    nivel = np.where(na_arte, nivel, np.float32(0.0))
    return nivel.astype(np.float32)


def _distancia(cor: np.ndarray, knockout: tuple[int, int, int]) -> np.ndarray:
    referencia = np.array(knockout, dtype=np.float32)
    diferenca = cor - referencia
    return np.sqrt(np.sum(diferenca * diferenca, axis=-1))


def _rampa_neutra(luma: np.ndarray) -> np.ndarray:
    """Verdadeiro onde o cinza muda por muitos tons, e não numa borda de dois tons."""
    amostra = np.clip(np.rint(luma * 255.0), 0, 255).astype(np.uint8)
    nucleo = np.ones((JANELA, JANELA), np.uint8)
    menor = cv2.erode(amostra, nucleo)
    maior = cv2.dilate(amostra, nucleo)
    faixa = maior.astype(np.int16) - menor.astype(np.int16)
    largo = faixa >= 8
    teto = menor.astype(np.int16) + (faixa * 3 // 4)
    piso = menor.astype(np.int16) + (faixa // 4)
    meio = ((amostra.astype(np.int16) > piso) & (amostra.astype(np.int16) < teto) & largo).astype(np.float32)
    proporcao = cv2.blur(meio, (JANELA, JANELA))
    return largo & (proporcao >= np.float32(0.35))
