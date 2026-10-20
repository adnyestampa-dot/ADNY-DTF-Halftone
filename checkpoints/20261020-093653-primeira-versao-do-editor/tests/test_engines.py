"""Testes dos motores. Não dependem da janela."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.engines.central import MotorCentral
from app.engines.cleanup_engine import aplicar as limpar
from app.engines.export_engine import alfa_binario, gravar_png
from app.engines.halftone_engine import renderizar
from app.engines.image_engine import polegadas_para_px, px_para_unidade
from app.engines.underbase_engine import construir
from app.model.dtx_store import carregar, salvar
from app.model.settings import Settings


class Retícula(unittest.TestCase):
    def test_recusa_fora_da_faixa(self) -> None:
        tom = np.full((30, 30), 0.5, np.float32)
        with self.assertRaises(ValueError):
            renderizar(tom, 19, 0, "square")
        with self.assertRaises(ValueError):
            renderizar(tom, 46, 0, "square")

    def test_quadrado_acompanha_a_cobertura(self) -> None:
        for cobertura, minimo, maximo in ((0.0, 0.0, 0.0), (0.5, 0.40, 0.60), (1.0, 1.0, 1.0)):
            tom = np.full((300, 300), cobertura, np.float32)
            tinta = renderizar(tom, 30, 0, "square")
            media = float(tinta.mean())
            self.assertGreaterEqual(media, minimo)
            self.assertLessEqual(media, maximo)

    def test_lpi_menor_gera_menos_pontos(self) -> None:
        tom = np.full((300, 300), 0.35, np.float32)
        import cv2

        def ilhas(tinta: np.ndarray) -> int:
            quantidade, _rotulos, _stats, _centros = cv2.connectedComponentsWithStats(
                tinta.astype(np.uint8), connectivity=8
            )
            return quantidade - 1

        self.assertLess(
            ilhas(renderizar(tom, 20, 0, "square")),
            ilhas(renderizar(tom, 45, 0, "square")),
        )

    def test_valor_usado_e_o_informado(self) -> None:
        ajustes = Settings(lpi=37, angle=22.5, dot_shape="circle")
        imagem = np.zeros((80, 80, 4), np.uint8)
        imagem[..., 0:3] = 255
        imagem[..., 3] = 255
        resultado = MotorCentral().processar(imagem, ajustes)
        self.assertEqual(resultado.lpi, 37)
        self.assertAlmostEqual(resultado.celula_px, 300 / 37)


class Separacao(unittest.TestCase):
    def test_preto_some_e_branco_fica_solido(self) -> None:
        imagem = np.zeros((120, 160, 4), np.uint8)
        imagem[..., 3] = 255
        imagem[30:90, 40:120] = (255, 255, 255, 255)
        ajustes = Settings(lpi=30, angle=0, dot_shape="square", mask_threshold=12, halftone_enabled=True)
        resultado = MotorCentral().processar(imagem, ajustes)
        self.assertTrue(alfa_binario(resultado.separacao))
        self.assertEqual(int(resultado.separacao[:20, :, 3].max()), 0)
        miolo = resultado.separacao[40:80, 50:110, 3]
        self.assertGreater(float((miolo == 255).mean()), 0.95)

    def test_choke_diminui_a_base(self) -> None:
        tinta = np.zeros((40, 40), dtype=bool)
        tinta[5:35, 5:35] = True
        sem = int((construir(tinta, 0)[..., 3] == 255).sum())
        com = int((construir(tinta, 2)[..., 3] == 255).sum())
        self.assertGreater(sem, com)

    def test_limpeza_remove_pixel_isolado(self) -> None:
        tinta = np.zeros((12, 12), dtype=bool)
        tinta[2, 2] = True
        tinta[4:9, 4:9] = True
        limpa = limpar(tinta, 2)
        self.assertFalse(limpa[2, 2])
        self.assertTrue(limpa[6, 6])

    def test_exportacao_e_projeto(self) -> None:
        imagem = np.zeros((60, 60, 4), np.uint8)
        imagem[..., 1] = 180
        imagem[..., 3] = 255
        imagem[:15, :, 0:3] = 0
        ajustes = Settings(underbase=True, choke_px=1, lpi=30, angle=0, dot_shape="line")
        resultado = MotorCentral().processar(imagem, ajustes)
        self.assertIsNotNone(resultado.base_branca)
        with tempfile.TemporaryDirectory() as pasta:
            png = Path(pasta) / "sep.png"
            gravar_png(png, resultado.separacao)
            projeto = Path(pasta) / "trabalho.dtx"
            salvar(projeto, imagem, ajustes, None, None)
            volta, lidos, _restaurar, _remover = carregar(projeto)
            self.assertEqual(tuple(volta.shape), tuple(imagem.shape))
            self.assertEqual(lidos.lpi, 30.0)
            self.assertTrue(lidos.underbase)

    def test_lpi_do_arquivo_nao_e_ajustado_em_silencio(self) -> None:
        with self.assertRaises(ValueError):
            Settings.from_dict({"lpi": 15, "dot_shape": "circle"})

    def test_medida_em_300_dpi(self) -> None:
        self.assertEqual(polegadas_para_px(2, "in"), 600)
        self.assertAlmostEqual(px_para_unidade(300, "in"), 1.0)


if __name__ == "__main__":
    unittest.main()
