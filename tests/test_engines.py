"""Testes dos motores. Não dependem da janela."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.engines.central import MotorCentral
from app.engines.cleanup_engine import aplicar as limpar
from app.engines.export_engine import alfa_binario, gravar_png
from app.engines.halftone_engine import renderizar
from app.engines.image_engine import carregar as carregar_imagem
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
    def test_chapado_fica_continuo_e_fumaca_vira_ponto(self) -> None:
        imagem = np.zeros((90, 240, 4), np.uint8)
        for coluna in range(240):
            valor = int(coluna / 239 * 255)
            imagem[:, coluna, 0:3] = valor
            imagem[:, coluna, 3] = 255
        imagem[10:50, 180:230] = (255, 214, 10, 255)
        imagem[60:85, 180:230] = (220, 20, 20, 128)
        ajustes = Settings(lpi=30, angle=0, dot_shape="square", mask_threshold=24)
        resultado = MotorCentral().processar(imagem, ajustes)
        self.assertEqual(int(resultado.separacao[:, :8, 3].max()), 0)
        amarelo = resultado.separacao[20:40, 195:215, 3]
        self.assertGreater(float((amarelo == 255).mean()), 0.98)
        cinza = resultado.tinta[0:8, 90:150]
        self.assertGreater(float(cinza.mean()), 0.15)
        self.assertLess(float(cinza.mean()), 0.85)
        fumaca = resultado.tinta[60:85, 190:220]
        self.assertGreater(float(fumaca.mean()), 0.25)
        self.assertLess(float(fumaca.mean()), 0.75)
        viva = np.zeros((40, 80, 4), np.uint8)
        viva[..., 3] = 255
        for coluna in range(80):
            viva[:, coluna] = (int(coluna / 79 * 255), 30, 255 - int(coluna / 79 * 255), 255)
        cores = MotorCentral().processar(viva, ajustes)
        self.assertGreater(float(cores.tinta[8:32, 20:60].mean()), 0.95)

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

    def test_arquivo_mantem_pixels_proporcao_e_dpi(self) -> None:
        imagem = np.zeros((40, 90, 4), np.uint8)
        imagem[..., 0] = 30
        imagem[..., 1] = 140
        imagem[..., 3] = 255
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "arte.png"
            Image.fromarray(imagem, "RGBA").save(origem, dpi=(144, 144))
            carregada, medida = carregar_imagem(origem)
            self.assertEqual(tuple(carregada.shape), tuple(imagem.shape))
            self.assertTrue(np.array_equal(carregada, imagem))
            self.assertEqual(medida.largura, 90)
            self.assertEqual(medida.altura, 40)
            self.assertAlmostEqual(medida.dpi_x, 144, delta=0.5)
            self.assertAlmostEqual(medida.dpi_y, 144, delta=0.5)
            ajustes = Settings(
                dpi=medida.dpi_x,
                dpi_y=medida.dpi_y,
                dpi_informado=True,
                lpi=36,
                angle=0,
                dot_shape="line",
            )
            resultado = MotorCentral().processar(carregada, ajustes)
            self.assertEqual(resultado.separacao.shape[:2], carregada.shape[:2])
            self.assertAlmostEqual(resultado.celula_px, 144 / 36, places=3)
            png = Path(pasta) / "saida.png"
            gravar_png(png, resultado.separacao, dpi=(medida.dpi_x, medida.dpi_y))
            with Image.open(png) as saida:
                self.assertEqual(saida.size, (90, 40))
                lido = saida.info["dpi"]
                self.assertAlmostEqual(float(lido[0]), float(medida.dpi_x), delta=0.5)
                self.assertAlmostEqual(float(lido[1]), float(medida.dpi_y), delta=0.5)

    def test_arquivo_sem_dpi_nao_recebe_300(self) -> None:
        imagem = np.zeros((12, 18, 4), np.uint8)
        imagem[..., 3] = 255
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "sem.png"
            Image.fromarray(imagem, "RGBA").save(origem)
            _carregada, medida = carregar_imagem(origem)
            self.assertIsNone(medida.dpi_x)
            self.assertIsNone(medida.dpi_y)
            png = Path(pasta) / "saida.png"
            gravar_png(png, imagem, dpi=None)
            with Image.open(png) as saida:
                self.assertEqual(saida.size, (18, 12))
                self.assertNotIn("dpi", saida.info)


if __name__ == "__main__":
    unittest.main()
