"""Entrada do executável; inicia o editor sem o monitor de desenvolvimento."""
from pathlib import Path
import json
import os
import sys
import time
import traceback

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def validar_executavel(destino: Path) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        import numpy as np
        from PIL import Image
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
        import app.ui.main_window as janela_modulo
        from app.engines.export_engine import alfa_binario
        from app.model.dtx_store import carregar

        raiz_real = janela_modulo.ROOT
        if getattr(sys, "frozen", False):
            assert not raiz_real.is_relative_to(Path(sys._MEIPASS)), "Dados na pasta temporaria"
        # O teste nunca sobrescreve projetos de uso real.
        janela_modulo.ROOT = destino / "dados-do-teste"
        q = QApplication.instance() or QApplication([])
        q.setQuitOnLastWindowClosed(False)
        janela = janela_modulo.JanelaPrincipal()
        janela.show()
        origem = np.zeros((180, 240, 4), dtype=np.uint8)
        origem[..., 3] = 255
        origem[25:125, 35:205] = (240, 35, 65, 255)
        origem[130:165, 35:205] = (200, 200, 200, 128)
        arquivo = destino / "entrada.png"
        Image.fromarray(origem).save(arquivo, dpi=(144, 144))
        janela.carregar_caminho(str(arquivo))
        janela.ajustes.underbase = True
        janela.ajustes.choke_px = 1
        janela._escrever_controles()
        janela._marcar()
        limite = time.monotonic() + 40
        while time.monotonic() < limite:
            q.processEvents()
            if (janela.preview is not None and janela.preview_rev == janela.edit_rev
                    and (janela.trabalhador is None or not janela.trabalhador.isRunning())):
                break
            time.sleep(0.02)
        else:
            raise TimeoutError("O processamento da interface nao terminou")
        assert janela.preview.lpi == 30
        assert alfa_binario(janela.preview.separacao)
        assert janela.preview.separacao.shape == origem.shape
        assert janela.preview.base_branca is not None
        janela._aplicar()
        saidas = janela.exportar_para(destino / "separacao.png")
        assert len(saidas) == 2 and all(p.is_file() for p in saidas)
        with Image.open(saidas[0]) as imagem:
            assert imagem.size == (240, 180)
            assert abs(imagem.info["dpi"][0] - 144) < 0.5
            assert set(np.unique(np.array(imagem)[..., 3])) <= {0, 255}
        janela._salvar_interno()
        projeto = janela_modulo.ROOT / "dados" / "projetos" / "projeto.dtx"
        volta, ajustes, _, _ = carregar(projeto)
        assert np.array_equal(volta, origem) and ajustes.underbase
        janela.botoes_vista["split"].click()
        q.processEvents()
        assert janela.grab().save(str(destino / "interface.png"))
        janela.close()
        janela.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        q.processEvents()
        resultado = {"ok": True, "frozen": bool(getattr(sys, "frozen", False)),
                     "interface": True, "processamento": True, "png": True,
                     "base_branca": True, "dtx_roundtrip": True,
                     "dpi": 144, "dimensoes": [240, 180],
                     "dados_persistentes": str(raiz_real), "python": sys.version}
        (destino / "resultado.json").write_text(json.dumps(resultado, indent=2), encoding="utf-8")
        return 0
    except Exception:
        (destino / "falha.txt").write_text(traceback.format_exc(), encoding="utf-8")
        return 1


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--smoke-test":
        raise SystemExit(validar_executavel(Path(sys.argv[2]).resolve()))
    from app.main import main
    raise SystemExit(main())
