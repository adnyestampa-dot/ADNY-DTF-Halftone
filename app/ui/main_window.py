"""Editor DTF. Os rótulos visíveis estão em português do Brasil, no vocabulário de serigrafia e DTF."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PySide6.QtCore import QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import NOME
from app.engines.central import MotorCentral
from app.engines.export_engine import gravar_mascara, gravar_png
from app.engines.image_engine import Origem, carregar, polegadas_para_px, px_para_unidade, recortar, redimensionar
from app.model.dtx_store import carregar as carregar_dtx
from app.model.dtx_store import salvar as salvar_dtx
from app.model.settings import SHAPE_LABELS, Settings
from app.ui.canvas import Tela
from app.ui.theme import CLARO, ESCURO
from app.ui.widgets import FaixaColorida, FaixaLevels, LinhaControle, Secao

ROOT = Path(__file__).resolve().parents[2]


class _Trabalhador(QThread):
    pronto = Signal(int, object)
    falhou = Signal(int, str)

    def __init__(self, job: int, rgba: np.ndarray, ajustes: Settings, restaurar, remover) -> None:
        super().__init__()
        self.job = job
        self.rgba = rgba
        self.ajustes = ajustes
        self.restaurar = restaurar
        self.remover = remover

    def run(self) -> None:
        try:
            resultado = MotorCentral().processar(self.rgba, self.ajustes, self.restaurar, self.remover)
            self.pronto.emit(self.job, resultado)
        except Exception as exc:
            self.falhou.emit(self.job, str(exc))


class JanelaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(NOME)
        self.resize(1440, 900)
        self.setAcceptDrops(True)
        self.ajustes = Settings()
        self.imagem: np.ndarray | None = None
        self.restaurar: np.ndarray | None = None
        self.remover: np.ndarray | None = None
        self.preview = None
        self.preview_rev = -1
        self.aplicado = None
        self.aplicado_ajustes: Settings | None = None
        self.edit_rev = 0
        self.aplicado_rev = -1
        self.job = 0
        self.trabalhador: _Trabalhador | None = None
        self.repetir = False
        self._interno = False
        self._proporcao = 1.0
        self.conta_gotas = ""
        self.tema_escuro = True
        self.vista = "original"
        self._montar()
        self._aplicar_tema()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._disparar)
        self._ligar()
        self._atualizar_botoes()
        self._pintar_amostras()

    def closeEvent(self, evento) -> None:
        if self.trabalhador is not None and self.trabalhador.isRunning():
            self.trabalhador.wait(8000)
        evento.accept()

    def _montar(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._cabecalho())
        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)
        corpo.addWidget(self._lateral())
        coluna = QVBoxLayout()
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(0)
        coluna.addWidget(self._vistas())
        coluna.addWidget(FaixaColorida())
        self.tela = Tela()
        coluna.addWidget(self.tela, 1)
        coluna.addWidget(self._rodape())
        corpo.addLayout(coluna, 1)
        raiz.addLayout(corpo, 1)

    def _cabecalho(self) -> QWidget:
        barra = QFrame()
        barra.setObjectName("cabecalho")
        barra.setFixedHeight(78)
        layout = QVBoxLayout(barra)
        layout.setContentsMargins(16, 8, 16, 6)
        layout.setSpacing(2)
        titulo = QLabel(NOME)
        titulo.setObjectName("titulo")
        layout.addWidget(titulo, 0, Qt.AlignmentFlag.AlignLeft)
        linha = QHBoxLayout()
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(4)
        self.arquivo = self._menu("Arquivo", self._menu_arquivo())
        self.tema = QPushButton("Claro")
        self.tema.setObjectName("neutro")
        self.estado = QLabel("●  Pronto")
        self.estado.setObjectName("estado")
        linha.addWidget(self.arquivo)
        linha.addWidget(self.tema)
        linha.addWidget(self.estado)
        linha.addStretch(1)
        layout.addLayout(linha)
        return barra

    def _menu(self, titulo: str, menu) -> QToolButton:
        botao = QToolButton()
        botao.setText(titulo)
        botao.setMenu(menu)
        botao.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        return botao

    def _menu_arquivo(self):
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Abrir", self._dialogo_abrir)
        menu.addAction("Fechar", self._fechar)
        self.acao_salvar = menu.addAction("Salvar", self._salvar_interno)
        menu.addAction("Exportar DTX", self._exportar_dtx)
        self.acao_exportar = QAction("Exportar PNG", self)
        self.acao_exportar.triggered.connect(self._dialogo_exportar)
        menu.addAction(self.acao_exportar)
        return menu

    def _vistas(self) -> QWidget:
        barra = QFrame()
        barra.setObjectName("cabecalho")
        layout = QHBoxLayout(barra)
        layout.setContentsMargins(12, 0, 12, 0)
        self.grupo_vistas = QButtonGroup(self)
        self.grupo_vistas.setExclusive(True)
        self.botoes_vista = {}
        for chave, texto in (
            ("original", "Original"),
            ("separation", "Separação"),
            ("split", "Lado a lado"),
            ("mask", "Máscara"),
        ):
            botao = QPushButton(texto)
            botao.setObjectName("vista")
            botao.setCheckable(True)
            self.grupo_vistas.addButton(botao)
            self.botoes_vista[chave] = botao
            layout.addWidget(botao)
        self.botoes_vista["original"].setChecked(True)
        layout.addSpacing(16)
        caixa = QFrame()
        caixa.setObjectName("fundoCamisa")
        linha = QHBoxLayout(caixa)
        linha.setContentsMargins(10, 2, 6, 2)
        linha.setSpacing(6)
        self.fundo_camisa = QCheckBox("Visualizar fundo da camisa")
        self.cor_fundo = QToolButton()
        self.cor_fundo.setObjectName("trocaCor")
        self.cor_fundo.setFixedSize(28, 28)
        self.cor_fundo.setToolTip("Mudar a cor do fundo da camisa")
        self.cor_fundo.setCursor(Qt.CursorShape.PointingHandCursor)
        linha.addWidget(self.fundo_camisa)
        linha.addWidget(self.cor_fundo)
        layout.addWidget(caixa)
        layout.addStretch(1)
        return barra

    def _lateral(self) -> QWidget:
        lateral = QFrame()
        lateral.setObjectName("lateral")
        lateral.setFixedWidth(320)
        coluna = QVBoxLayout(lateral)
        coluna.setContentsMargins(12, 12, 12, 12)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        conteudo = QWidget()
        self.painel = QVBoxLayout(conteudo)
        self.painel.setContentsMargins(0, 0, 8, 0)
        self._controles()
        self.painel.addStretch(1)
        rolagem.setWidget(conteudo)
        coluna.addWidget(rolagem, 1)
        self.resetar = QPushButton("Restaurar ajustes")
        self.resetar.setObjectName("neutro")
        self.aplicar = QPushButton("✓   Aplicar separação")
        self.aplicar.setObjectName("primario")
        self.exportar = QPushButton("Exportar PNG")
        self.exportar.setObjectName("secundario")
        self.dica = QLabel("Aplique a separação para liberar a exportação")
        self.dica.setObjectName("dica")
        self.dica.setWordWrap(True)
        self.dica.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coluna.addWidget(self.resetar)
        coluna.addWidget(self.aplicar)
        coluna.addWidget(self.exportar)
        coluna.addWidget(self.dica)
        return lateral

    def _controles(self) -> None:
        self.painel.addWidget(Secao("Retícula", self._halftone(), aberta=True))
        self.painel.addWidget(Secao("Níveis", self._levels()))
        self.painel.addWidget(Secao("Tamanho da arte", self._tamanho()))
        self.painel.addWidget(Secao("Recorte", self._recorte()))
        self.painel.addWidget(Secao("Cor da camiseta", self._camisa()))
        self.painel.addWidget(Secao("Ajuste de cor", self._ajustes_cor()))
        self.painel.addWidget(Secao("Limpeza", self._limpeza()))
        self.painel.addWidget(Secao("Base branca", self._base()))
        self.painel.addWidget(Secao("Camadas", self._camadas()))

    def _halftone(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.habilitar = QCheckBox("Usar retícula")
        self.habilitar.setChecked(True)
        presets = QHBoxLayout()
        self.preset_branco = QPushButton("Branca")
        self.preset_cor = QPushButton("Colorida")
        self.preset_preto = QPushButton("Preta")
        for botao in (self.preset_branco, self.preset_cor, self.preset_preto):
            botao.setObjectName("neutro")
            presets.addWidget(botao)
        self.lpi = QComboBox()
        for valor in range(20, 46):
            texto = "30 lpi    Padrão" if valor == 30 else f"{valor} lpi"
            self.lpi.addItem(texto, valor)
        self.lpi.setCurrentIndex(10)
        self.angulo = QDoubleSpinBox()
        self.angulo.setRange(0, 90)
        self.angulo.setDecimals(1)
        self.angulo.setSingleStep(0.5)
        self.angulo.setValue(22.5)
        self.angulo.setSuffix("°")
        self.forma = QComboBox()
        for chave, rotulo in SHAPE_LABELS.items():
            self.forma.addItem(rotulo, chave)
        layout.addWidget(self.habilitar)
        layout.addLayout(presets)
        layout.addWidget(LinhaControle("Lineatura", self.lpi))
        layout.addWidget(LinhaControle("Ângulo", self.angulo))
        layout.addWidget(LinhaControle("Formato do ponto", self.forma))
        return caixa

    def _levels(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        layout.addWidget(QLabel("Níveis de entrada"))
        self.entrada = FaixaLevels(True, True)
        layout.addWidget(self.entrada)
        layout.addWidget(QLabel("Níveis de saída"))
        self.saida = FaixaLevels(False, False)
        layout.addWidget(self.saida)
        self.limiar, self.limiar_texto = self._slider(0, 255, 24, lambda valor: str(valor))
        layout.addWidget(LinhaControle("Limiar da máscara", self._com_legenda(self.limiar, self.limiar_texto)))
        pontos = QHBoxLayout()
        self.ponto_preto = QPushButton("Ponto preto")
        self.ponto_branco = QPushButton("Ponto branco")
        for botao in (self.ponto_preto, self.ponto_branco):
            botao.setObjectName("neutro")
            pontos.addWidget(botao)
        layout.addLayout(pontos)
        return caixa

    def _tamanho(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.largura = self._decimal()
        self.altura = self._decimal()
        self.travar = QCheckBox("Travar proporção")
        self.travar.setChecked(True)
        self.unidades = QComboBox()
        self.unidades.addItems(["pol", "cm", "mm"])
        self.aplicar_tamanho = QPushButton("Aplicar tamanho")
        self.aplicar_tamanho.setObjectName("neutro")
        layout.addWidget(LinhaControle("Largura", self.largura))
        layout.addWidget(LinhaControle("Altura", self.altura))
        layout.addWidget(self.travar)
        layout.addWidget(LinhaControle("Unidade", self.unidades))
        layout.addWidget(self.aplicar_tamanho)
        return caixa

    def _recorte(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.botao_recorte = QPushButton("Recortar arte")
        self.confirmar_recorte = QPushButton("Confirmar recorte")
        self.cancelar_recorte = QPushButton("Cancelar")
        for botao in (self.botao_recorte, self.confirmar_recorte, self.cancelar_recorte):
            botao.setObjectName("neutro")
        layout.addWidget(self.botao_recorte)
        linha = QHBoxLayout()
        linha.addWidget(self.confirmar_recorte)
        linha.addWidget(self.cancelar_recorte)
        layout.addLayout(linha)
        return caixa

    def _camisa(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.amostra_knockout = QPushButton("Cor a vazar")
        self.amostra_camisa = QPushButton("Cor da camiseta")
        for botao in (self.amostra_knockout, self.amostra_camisa):
            botao.setObjectName("neutro")
        self.vincular = QCheckBox("Vazar a cor da camiseta")
        self.vincular.setChecked(True)
        self.preview_camisa = QCheckBox("Ver na camiseta")
        layout.addWidget(self.amostra_knockout)
        layout.addWidget(self.amostra_camisa)
        layout.addWidget(self.vincular)
        layout.addWidget(self.preview_camisa)
        return caixa

    def _ajustes_cor(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.matiz, self.matiz_texto = self._slider(-180, 180, 0, lambda valor: str(valor))
        self.saturacao, self.saturacao_texto = self._slider(-100, 100, 0, lambda valor: str(valor))
        self.luminosidade, self.luminosidade_texto = self._slider(-100, 100, 0, lambda valor: str(valor))
        layout.addWidget(LinhaControle("Matiz", self._com_legenda(self.matiz, self.matiz_texto)))
        layout.addWidget(LinhaControle("Saturação", self._com_legenda(self.saturacao, self.saturacao_texto)))
        layout.addWidget(LinhaControle("Luminosidade", self._com_legenda(self.luminosidade, self.luminosidade_texto)))
        return caixa

    def _limpeza(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.limpeza, self.limpeza_texto = self._slider(0, 100, 0, lambda valor: f"{valor} px")
        layout.addWidget(QLabel("Pontos soltos"))
        layout.addWidget(self.limpeza)
        layout.addWidget(self.limpeza_texto)
        return caixa

    def _base(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.base_ligada = QCheckBox("Gerar base branca")
        self.choke = QComboBox()
        for valor in (0, 1, 2):
            self.choke.addItem(f"{valor} px", valor)
        self.modo_branco = QComboBox()
        self.modo_branco.addItem("Camada", "layer")
        self.modo_branco.addItem("Máscara", "mask")
        self.modo_branco.addItem("Canal spot", "spot")
        layout.addWidget(self.base_ligada)
        layout.addWidget(LinhaControle("Redução da base", self.choke))
        layout.addWidget(LinhaControle("Gravar a base como", self.modo_branco))
        return caixa

    def _camadas(self) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(4, 0, 0, 0)
        self.pincel = QPushButton("Pincel")
        self.varinha = QPushButton("Varinha mágica")
        for botao in (self.pincel, self.varinha):
            botao.setObjectName("neutro")
            botao.setCheckable(True)
        self.raio = QSpinBox()
        self.raio.setRange(1, 80)
        self.raio.setValue(24)
        self.raio.setSuffix(" px")
        self.tolerancia = QSpinBox()
        self.tolerancia.setRange(0, 128)
        self.tolerancia.setValue(32)
        layout.addWidget(self.pincel)
        layout.addWidget(LinhaControle("Raio do pincel", self.raio))
        layout.addWidget(self.varinha)
        layout.addWidget(LinhaControle("Tolerância da varinha", self.tolerancia))
        return caixa

    def _rodape(self) -> QWidget:
        barra = QFrame()
        barra.setObjectName("rodape")
        barra.setFixedHeight(48)
        layout = QHBoxLayout(barra)
        self.medidas = QLabel("")
        self.medidas.setObjectName("medidas")
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(5, 400)
        self.zoom.setValue(100)
        self.zoom.setFixedWidth(160)
        self.cem = QPushButton("100%")
        self.ajustar = QPushButton("Ajustar à tela")
        for botao in (self.cem, self.ajustar):
            botao.setObjectName("neutro")
        layout.addWidget(self.medidas)
        layout.addStretch(1)
        layout.addWidget(self.zoom)
        layout.addWidget(self.cem)
        layout.addWidget(self.ajustar)
        return barra

    def _slider(self, minimo: int, maximo: int, valor: int, formato) -> tuple[QSlider, QLabel]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimo, maximo)
        slider.setValue(valor)
        texto = QLabel(formato(valor))
        slider.valueChanged.connect(lambda novo, rotulo=texto, fn=formato: rotulo.setText(fn(novo)))
        return slider, texto

    def _com_legenda(self, slider: QSlider, texto: QLabel) -> QWidget:
        caixa = QWidget()
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(slider)
        layout.addWidget(texto)
        return caixa

    def _decimal(self) -> QDoubleSpinBox:
        campo = QDoubleSpinBox()
        campo.setRange(0.01, 80)
        campo.setDecimals(2)
        campo.setValue(1)
        return campo

    def _ligar(self) -> None:
        self.tema.clicked.connect(self._trocar_tema)
        self.tela.abrir_pedido.connect(self._dialogo_abrir)
        self.tela.zoom_mudou.connect(self._zoom_externo)
        self.tela.amostra.connect(self._usar_amostra)
        self.tela.pincel.connect(self._pintar)
        self.tela.varinha.connect(self._varinha)
        self.zoom.valueChanged.connect(self._zoom_manual)
        self.cem.clicked.connect(self.tela.zoom_real)
        self.ajustar.clicked.connect(self.tela.ajustar_tela)
        for chave, botao in self.botoes_vista.items():
            botao.clicked.connect(lambda _marcado=False, nome=chave: self._definir_vista(nome))
        self.habilitar.toggled.connect(self._marcar)
        self.lpi.currentIndexChanged.connect(self._marcar)
        self.angulo.valueChanged.connect(self._marcar)
        self.forma.currentIndexChanged.connect(self._marcar)
        self.entrada.alterado.connect(self._marcar)
        self.saida.alterado.connect(self._marcar)
        self.limiar.valueChanged.connect(self._marcar)
        self.matiz.valueChanged.connect(self._marcar)
        self.saturacao.valueChanged.connect(self._marcar)
        self.luminosidade.valueChanged.connect(self._marcar)
        self.limpeza.valueChanged.connect(self._marcar)
        self.base_ligada.toggled.connect(self._marcar)
        self.choke.currentIndexChanged.connect(self._marcar)
        self.modo_branco.currentIndexChanged.connect(self._marcar)
        self.largura.valueChanged.connect(self._sincronizar_altura)
        self.unidades.currentIndexChanged.connect(self._trocar_unidade)
        self.aplicar_tamanho.clicked.connect(self._aplicar_tamanho)
        self.botao_recorte.clicked.connect(self._entrar_recorte)
        self.confirmar_recorte.clicked.connect(self._confirmar_recorte)
        self.cancelar_recorte.clicked.connect(self._cancelar_recorte)
        self.amostra_knockout.clicked.connect(lambda: self._armar_conta_gotas("knockout"))
        self.amostra_camisa.clicked.connect(lambda: self._armar_conta_gotas("shirt"))
        self.ponto_preto.clicked.connect(lambda: self._armar_conta_gotas("black"))
        self.ponto_branco.clicked.connect(lambda: self._armar_conta_gotas("white"))
        self.preview_camisa.toggled.connect(self._alternar_preview_camisa)
        self.fundo_camisa.toggled.connect(self._alternar_preview_camisa)
        self.cor_fundo.clicked.connect(self._escolher_cor_fundo)
        self.preset_branco.clicked.connect(lambda: self._preset("white"))
        self.preset_cor.clicked.connect(lambda: self._preset("color"))
        self.preset_preto.clicked.connect(lambda: self._preset("black"))
        self.resetar.clicked.connect(self._resetar)
        self.aplicar.clicked.connect(self._aplicar)
        self.exportar.clicked.connect(self._dialogo_exportar)
        self.pincel.toggled.connect(self._armar_pincel)
        self.varinha.toggled.connect(self._armar_varinha)
        self.raio.valueChanged.connect(self._atualizar_raio)

    def _aplicar_tema(self) -> None:
        self.setStyleSheet(ESCURO if self.tema_escuro else CLARO)
        self.tema.setText("Claro" if self.tema_escuro else "Escuro")

    def _trocar_tema(self) -> None:
        self.tema_escuro = not self.tema_escuro
        self._aplicar_tema()

    def dragEnterEvent(self, evento) -> None:
        if evento.mimeData().hasUrls():
            evento.acceptProposedAction()

    def dropEvent(self, evento) -> None:
        urls = evento.mimeData().urls()
        if urls:
            self.carregar_caminho(urls[0].toLocalFile())

    def carregar_caminho(self, caminho: str) -> None:
        if caminho.lower().endswith(".dtx"):
            try:
                rgba, ajustes, restaurar, remover = carregar_dtx(caminho)
            except Exception as exc:
                QMessageBox.warning(self, "Abrir", str(exc))
                return
            self.ajustes = ajustes
            self._escrever_controles()
            self._receber_imagem(rgba, restaurar, remover)
            return
        try:
            rgba, origem = carregar(caminho)
        except Exception as exc:
            QMessageBox.warning(self, "Abrir", str(exc))
            return
        self._aplicar_origem(origem)
        self._receber_imagem(rgba, None, None)

    def carregar_array(self, rgba: np.ndarray) -> None:
        self._aplicar_origem(Origem(int(rgba.shape[1]), int(rgba.shape[0]), None, None))
        self._receber_imagem(np.asarray(rgba), None, None)

    def _aplicar_origem(self, origem: Origem) -> None:
        if origem.dpi_x is None or origem.dpi_y is None:
            self.ajustes.dpi = 300.0
            self.ajustes.dpi_y = None
            self.ajustes.dpi_informado = False
            return
        self.ajustes.dpi = float(origem.dpi_x)
        self.ajustes.dpi_y = float(origem.dpi_y)
        self.ajustes.dpi_informado = True

    def _eixos_dpi(self) -> tuple[float, float] | None:
        if not self.ajustes.dpi_informado or self.ajustes.dpi is None:
            return None
        eixo_x = float(self.ajustes.dpi)
        eixo_y = float(self.ajustes.dpi_y if self.ajustes.dpi_y is not None else eixo_x)
        return eixo_x, eixo_y

    def _receber_imagem(self, rgba: np.ndarray, restaurar, remover) -> None:
        self.imagem = np.ascontiguousarray(rgba)
        altura, largura = self.imagem.shape[:2]
        self._proporcao = largura / max(1, altura)
        self.restaurar = restaurar
        self.remover = remover
        self.preview = None
        self.preview_rev = -1
        self.aplicado = None
        self.aplicado_rev = -1
        self.vista = "original"
        self.botoes_vista["original"].setChecked(True)
        self._atualizar_medidas()
        self._histograma()
        self._mostrar()
        self._marcar()

    def _fechar(self) -> None:
        self.imagem = None
        self.restaurar = None
        self.remover = None
        self.preview = None
        self.preview_rev = -1
        self.aplicado = None
        self.aplicado_rev = -1
        self.tela.definir_imagens("original", None)
        self.medidas.setText("")
        self._atualizar_botoes()

    def _dialogo_abrir(self) -> None:
        caminho, _filtro = QFileDialog.getOpenFileName(
            self,
            "Abrir",
            str(ROOT),
            "Arte (*.png *.jpg *.jpeg *.dtx)",
        )
        if caminho:
            self.carregar_caminho(caminho)

    def _ler_controles(self) -> None:
        self.ajustes.halftone_enabled = self.habilitar.isChecked()
        self.ajustes.lpi = float(self.lpi.currentData())
        self.ajustes.angle = float(self.angulo.value())
        self.ajustes.dot_shape = self.forma.currentData()
        self.ajustes.input_black = int(self.entrada.preto)
        self.ajustes.input_white = int(self.entrada.branco)
        self.ajustes.gamma = float(self.entrada.gamma)
        self.ajustes.output_black = int(self.saida.preto)
        self.ajustes.output_white = int(self.saida.branco)
        self.ajustes.mask_threshold = int(self.limiar.value())
        self.ajustes.hue = float(self.matiz.value())
        self.ajustes.saturation = float(self.saturacao.value())
        self.ajustes.lightness = float(self.luminosidade.value())
        self.ajustes.cleanup = int(self.limpeza.value())
        self.ajustes.underbase = self.base_ligada.isChecked()
        self.ajustes.choke_px = int(self.choke.currentData())
        self.ajustes.white_mode = self.modo_branco.currentData()
        self.ajustes.link_shirt = self.vincular.isChecked()
        self.ajustes.shirt_preview = self.preview_camisa.isChecked()
        self.ajustes.validate()

    def _escrever_controles(self) -> None:
        self._interno = True
        self.habilitar.setChecked(self.ajustes.halftone_enabled)
        indice = self.lpi.findData(int(self.ajustes.lpi))
        if indice >= 0:
            self.lpi.setCurrentIndex(indice)
        self.angulo.setValue(float(self.ajustes.angle))
        forma = self.forma.findData(self.ajustes.dot_shape)
        if forma >= 0:
            self.forma.setCurrentIndex(forma)
        self.entrada.definir(self.ajustes.input_black, self.ajustes.input_white, self.ajustes.gamma)
        self.saida.definir(self.ajustes.output_black, self.ajustes.output_white)
        self.limiar.setValue(int(self.ajustes.mask_threshold))
        self.matiz.setValue(int(self.ajustes.hue))
        self.saturacao.setValue(int(self.ajustes.saturation))
        self.luminosidade.setValue(int(self.ajustes.lightness))
        self.limpeza.setValue(int(self.ajustes.cleanup))
        self.base_ligada.setChecked(self.ajustes.underbase)
        choke = self.choke.findData(int(self.ajustes.choke_px))
        if choke >= 0:
            self.choke.setCurrentIndex(choke)
        modo = self.modo_branco.findData(self.ajustes.white_mode)
        if modo >= 0:
            self.modo_branco.setCurrentIndex(modo)
        self.vincular.setChecked(self.ajustes.link_shirt)
        self.preview_camisa.setChecked(self.ajustes.shirt_preview)
        self.fundo_camisa.setChecked(self.ajustes.shirt_preview)
        self._interno = False
        self._pintar_amostras()

    def _marcar(self, *_args) -> None:
        if self._interno or self.imagem is None:
            self._atualizar_botoes()
            return
        try:
            self._ler_controles()
        except ValueError as exc:
            self.estado.setText(str(exc))
            return
        self.edit_rev += 1
        self._atualizar_botoes()
        self.estado.setText("●  Separando")
        self.timer.start(80)

    def _disparar(self) -> None:
        if self.imagem is None:
            return
        if self.trabalhador and self.trabalhador.isRunning():
            self.repetir = True
            return
        self.job += 1
        job = self.job
        ajustes = Settings.from_dict(self.ajustes.to_dict())
        restaurar = None if self.restaurar is None else self.restaurar.copy()
        remover = None if self.remover is None else self.remover.copy()
        self.trabalhador = _Trabalhador(job, self.imagem.copy(), ajustes, restaurar, remover)
        self.trabalhador.rev = self.edit_rev
        self.trabalhador.pronto.connect(self._resultado)
        self.trabalhador.falhou.connect(self._falha)
        self.trabalhador.start()

    def _resultado(self, job: int, resultado) -> None:
        if job != self.job:
            return
        if self.trabalhador is not None and self.trabalhador.rev == self.edit_rev:
            self.preview = resultado
            self.preview_rev = self.trabalhador.rev
            self._registrar(resultado)
            self._mostrar()
        self.estado.setText("●  Pronto")
        self._atualizar_botoes()
        if self.repetir:
            self.repetir = False
            self._disparar()

    def _falha(self, job: int, mensagem: str) -> None:
        if job != self.job:
            return
        self.estado.setText("●  Pronto")
        QMessageBox.warning(self, "Separação", mensagem)

    def _registrar(self, resultado) -> None:
        pasta = ROOT / "dados"
        pasta.mkdir(parents=True, exist_ok=True)
        registro = {
            "lpi": resultado.lpi,
            "celula_px": resultado.celula_px,
            "alfa_binario": True,
            "base_branca": resultado.base_branca is not None,
        }
        (pasta / "ultimo_processamento.json").write_text(
            json.dumps(registro, indent=2),
            encoding="utf-8",
        )

    def _definir_vista(self, nome: str) -> None:
        self.vista = nome
        self._mostrar()

    def _mostrar(self) -> None:
        if self.imagem is None:
            self.tela.definir_imagens("original", None)
            return
        modo = self.vista
        original = self._sobrepor(self.imagem)
        if self.preview is None:
            self.tela.definir_imagens("original" if modo != "split" else "split", original, original)
            return
        separacao = self._sobrepor(self.preview.separacao)
        mascara = np.zeros_like(self.preview.separacao)
        mascara[..., 3] = np.where(self.preview.tinta, 255, 0)
        mascara = self._sobrepor(mascara)
        if modo == "original":
            self.tela.definir_imagens("original", original)
        elif modo == "mask":
            self.tela.definir_imagens("mask", mascara)
        elif modo == "split":
            self.tela.definir_imagens("split", original, separacao)
        else:
            self.tela.definir_imagens("separation", separacao)
        self._rodape_texto()

    def _sobrepor(self, arte: np.ndarray) -> np.ndarray:
        altura, largura = arte.shape[:2]
        pixels = np.ascontiguousarray(arte)
        if pixels.shape[2] == 4 and not np.any(pixels[..., 3]) and np.any(pixels[..., 0:3]):
            pixels = pixels.copy()
            pixels[..., 3] = 255
        if self.ajustes.shirt_preview:
            fundo = np.empty((altura, largura, 3), np.float32)
            fundo[..., 0] = float(self.ajustes.shirt[0])
            fundo[..., 1] = float(self.ajustes.shirt[1])
            fundo[..., 2] = float(self.ajustes.shirt[2])
        else:
            yy, xx = np.indices((altura, largura))
            claro = ((xx // 16 + yy // 16) % 2) == 0
            tom = np.where(claro, np.float32(214), np.float32(168))
            fundo = np.stack((tom, tom, tom), axis=-1)
        alfa = pixels[..., 3:4].astype(np.float32) / np.float32(255.0)
        cor = pixels[..., 0:3].astype(np.float32)
        mistura = cor * alfa + fundo * (np.float32(1.0) - alfa)
        saida = np.empty((altura, largura, 4), np.uint8)
        saida[..., 0:3] = np.clip(np.rint(mistura), 0, 255).astype(np.uint8)
        saida[..., 3] = 255
        return saida

    def _histograma(self) -> None:
        if self.imagem is None:
            return
        rgb = self.imagem[..., 0:3].astype(np.float32)
        luma = np.rint(0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).astype(np.uint8)
        self.entrada.definir_histograma(np.bincount(luma.ravel(), minlength=256))

    def _atual_para_exportar(self):
        if self.preview is not None and self.preview_rev == self.edit_rev:
            return self.preview, self.ajustes
        if self.aplicado is not None and self.aplicado_rev == self.edit_rev:
            return self.aplicado, self.aplicado_ajustes or self.ajustes
        return None, None

    def _atualizar_botoes(self) -> None:
        tem_imagem = self.imagem is not None
        resultado, _ajustes = self._atual_para_exportar()
        self.aplicar.setEnabled(resultado is not None)
        self.exportar.setEnabled(resultado is not None)
        self.acao_exportar.setEnabled(resultado is not None)
        if hasattr(self, "acao_salvar"):
            self.acao_salvar.setEnabled(tem_imagem)
        if not tem_imagem or resultado is not None:
            self.dica.setText("")
        else:
            self.dica.setText("Aguarde a separação para exportar")

    def _rodape_texto(self) -> None:
        if self.imagem is None:
            self.medidas.setText("")
            return
        altura, largura = self.imagem.shape[:2]
        eixos = self._eixos_dpi()
        if eixos is None:
            marca = "DPI não informado"
        elif abs(eixos[0] - eixos[1]) < 0.05:
            marca = f"{eixos[0]:g} DPI"
        else:
            marca = f"{eixos[0]:g}×{eixos[1]:g} DPI"
        self.medidas.setText(f"{largura}×{altura}  ·  {marca}  ·  {self.tela.percentual()}%")

    def _zoom_externo(self, percentual: int) -> None:
        self._interno = True
        self.zoom.setValue(max(5, min(400, percentual)))
        self._interno = False
        self._rodape_texto()

    def _zoom_manual(self, valor: int) -> None:
        if self._interno:
            return
        self.tela.definir_zoom(valor)

    def _preset(self, nome: str) -> None:
        self.ajustes.halftone_enabled = True
        self.ajustes.lpi = 30
        self.ajustes.angle = 22.5
        self.ajustes.dot_shape = "circle"
        if nome == "black":
            self.ajustes.knockout = (0, 0, 0)
            self.ajustes.shirt = (0, 0, 0)
            self.ajustes.link_shirt = True
            self.ajustes.shirt_preview = True
        elif nome == "white":
            self.ajustes.knockout = (255, 255, 255)
            self.ajustes.shirt = (255, 255, 255)
            self.ajustes.link_shirt = True
            self.ajustes.shirt_preview = True
        self._escrever_controles()
        self._marcar()

    def _resetar(self) -> None:
        camisa = self.ajustes.shirt
        knockout = self.ajustes.knockout
        dpi = self.ajustes.dpi
        dpi_y = self.ajustes.dpi_y
        informado = self.ajustes.dpi_informado
        self.ajustes = Settings(
            shirt=camisa,
            knockout=knockout,
            dpi=dpi,
            dpi_y=dpi_y,
            dpi_informado=informado,
        )
        self._escrever_controles()
        self._marcar()

    def _aplicar(self) -> None:
        if self.preview is None:
            return
        self.aplicado = self.preview
        self.aplicado_ajustes = Settings.from_dict(self.ajustes.to_dict())
        self.aplicado_rev = self.edit_rev
        self._atualizar_botoes()

    def _dialogo_exportar(self) -> None:
        resultado, ajustes = self._atual_para_exportar()
        if resultado is None or ajustes is None:
            self.estado.setText("●  Aguarde a separação")
            return
        caminho, _filtro = QFileDialog.getSaveFileName(self, "Exportar PNG", str(ROOT / "separacao.png"), "PNG (*.png)")
        if not caminho:
            return
        self.aplicado = resultado
        self.aplicado_ajustes = Settings.from_dict(ajustes.to_dict())
        self.aplicado_rev = self.edit_rev
        try:
            self.exportar_para(Path(caminho))
        except Exception as exc:
            self.estado.setText("●  PNG não exportado")
            QMessageBox.warning(self, "Exportar PNG", str(exc))
            return
        self.estado.setText("●  PNG exportado")
        self._atualizar_botoes()

    def exportar_para(self, caminho: Path) -> list[Path]:
        if self.aplicado is None or self.aplicado_ajustes is None:
            raise RuntimeError("A separação ainda não está pronta para exportar.")
        caminho = Path(caminho)
        if self.imagem is not None and self.aplicado.separacao.shape[:2] != self.imagem.shape[:2]:
            raise RuntimeError("A separação saiu com tamanho diferente da arte.")
        dpi = self._eixos_dpi()
        gravar_png(caminho, self.aplicado.separacao, dpi=dpi)
        gravados = [caminho]
        if self.aplicado.base_branca is not None:
            modo = self.aplicado_ajustes.white_mode
            sufixo = {"layer": "_white.png", "mask": "_mask.png", "spot": "_spot.png"}[modo]
            destino = caminho.with_name(caminho.stem + sufixo)
            if modo == "mask":
                gravar_mascara(destino, self.aplicado.base_branca, dpi=dpi)
            else:
                gravar_png(destino, self.aplicado.base_branca, modo_branco=modo, dpi=dpi)
            gravados.append(destino)
        return gravados

    def _salvar_interno(self) -> None:
        if self.imagem is None:
            self.estado.setText("●  Abra uma arte para salvar")
            return
        pasta = ROOT / "dados" / "projetos"
        destino = pasta / "projeto.dtx"
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            salvar_dtx(destino, self.imagem, self.ajustes, self.restaurar, self.remover)
        except Exception as exc:
            self.estado.setText("●  Não salvou")
            QMessageBox.warning(self, "Salvar", str(exc))
            return
        self.estado.setText("●  Projeto salvo")
        self.estado.setToolTip(str(destino))

    def _exportar_dtx(self) -> None:
        if self.imagem is None:
            return
        caminho, _filtro = QFileDialog.getSaveFileName(self, "Exportar DTX", str(ROOT / "projeto.dtx"), "DTX (*.dtx)")
        if caminho:
            salvar_dtx(caminho, self.imagem, self.ajustes, self.restaurar, self.remover)

    def _atualizar_medidas(self) -> None:
        if self.imagem is None:
            return
        altura, largura = self.imagem.shape[:2]
        unidade = self.unidades.currentText()
        eixos = self._eixos_dpi()
        self.aplicar_tamanho.setEnabled(eixos is not None)
        self._interno = True
        if eixos is None:
            self.largura.setValue(largura)
            self.altura.setValue(altura)
        else:
            self.largura.setValue(px_para_unidade(largura, unidade, eixos[0]))
            self.altura.setValue(px_para_unidade(altura, unidade, eixos[1]))
        self._interno = False
        self.tela.unidade = unidade
        self._rodape_texto()

    def _trocar_unidade(self) -> None:
        self._atualizar_medidas()

    def _sincronizar_altura(self, valor: float) -> None:
        if self._interno or not self.travar.isChecked() or self._proporcao <= 0:
            return
        self._interno = True
        self.altura.setValue(valor / self._proporcao)
        self._interno = False

    def _aplicar_tamanho(self) -> None:
        if self.imagem is None:
            return
        eixos = self._eixos_dpi()
        if eixos is None:
            self.estado.setText("●  DPI não informado")
            return
        unidade = self.unidades.currentText()
        largura = polegadas_para_px(self.largura.value(), unidade, eixos[0])
        altura = polegadas_para_px(self.altura.value(), unidade, eixos[1])
        self.imagem = redimensionar(self.imagem, largura, altura)
        self.restaurar = None
        self.remover = None
        self._proporcao = largura / max(1, altura)
        self._histograma()
        self._marcar()

    def _entrar_recorte(self) -> None:
        if self.imagem is None:
            return
        altura, largura = self.imagem.shape[:2]
        from PySide6.QtCore import QRect

        self.tela.iniciar_recorte(QRect(0, 0, largura, altura))

    def _confirmar_recorte(self) -> None:
        if self.imagem is None or self.tela.recorte is None:
            return
        rect = self.tela.recorte
        self.imagem = recortar(self.imagem, rect.x(), rect.y(), rect.width(), rect.height())
        self.restaurar = None
        self.remover = None
        self.tela.ferramenta = "navegar"
        self.tela.recorte = None
        altura, largura = self.imagem.shape[:2]
        self._proporcao = largura / max(1, altura)
        self._atualizar_medidas()
        self._histograma()
        self._marcar()

    def _cancelar_recorte(self) -> None:
        self.tela.ferramenta = "navegar"
        self.tela.recorte = None
        self.tela.update()

    def _alternar_preview_camisa(self, ligado: bool) -> None:
        if self._interno:
            return
        self._interno = True
        self.ajustes.shirt_preview = bool(ligado)
        self.preview_camisa.setChecked(self.ajustes.shirt_preview)
        self.fundo_camisa.setChecked(self.ajustes.shirt_preview)
        self._interno = False
        self._mostrar()

    def _escolher_cor_fundo(self) -> None:
        atual = QColor(*[int(canal) for canal in self.ajustes.shirt])
        cor = QColorDialog.getColor(atual, self, "Cor do fundo da camisa")
        if not cor.isValid():
            return
        self._definir_cor_fundo((cor.red(), cor.green(), cor.blue()))

    def _definir_cor_fundo(self, cor: tuple) -> None:
        self.ajustes.shirt = (int(cor[0]), int(cor[1]), int(cor[2]))
        self.ajustes.link_shirt = False
        self._interno = True
        self.vincular.setChecked(False)
        self._interno = False
        self._pintar_amostras()
        self._mostrar()

    def _icone_troca_cor(self, cor: tuple) -> QIcon:
        pixmap = QPixmap(22, 22)
        pixmap.fill(Qt.GlobalColor.transparent)
        pintor = QPainter(pixmap)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        claro = int(cor[0]) + int(cor[1]) + int(cor[2]) > 380
        traco = QColor("#1c1e22" if claro else "#f4f5f7")
        pintor.setPen(QPen(traco, 1.4))
        pintor.setBrush(QColor(int(cor[0]), int(cor[1]), int(cor[2])))
        pintor.drawEllipse(1, 2, 13, 13)
        pintor.setPen(QPen(traco, 1.7))
        pintor.drawLine(12, 16, 19, 9)
        pintor.drawLine(17, 7, 20, 10)
        pintor.end()
        return QIcon(pixmap)

    def _armar_conta_gotas(self, destino: str) -> None:
        self.conta_gotas = destino
        self.tela.ferramenta = "conta-gotas"
        self.pincel.setChecked(False)
        self.varinha.setChecked(False)

    def _usar_amostra(self, x: int, y: int) -> None:
        if self.imagem is None:
            return
        pixel = self.imagem[y, x]
        cor = (int(pixel[0]), int(pixel[1]), int(pixel[2]))
        if self.conta_gotas == "knockout":
            self.ajustes.knockout = cor
            if self.vincular.isChecked():
                self.ajustes.shirt = cor
        elif self.conta_gotas == "shirt":
            self.ajustes.shirt = cor
            self.ajustes.link_shirt = False
            self.vincular.setChecked(False)
        elif self.conta_gotas == "black":
            luma = int(round(0.2126 * cor[0] + 0.7152 * cor[1] + 0.0722 * cor[2]))
            self.entrada.definir(luma, self.entrada.branco, self.entrada.gamma)
        elif self.conta_gotas == "white":
            luma = int(round(0.2126 * cor[0] + 0.7152 * cor[1] + 0.0722 * cor[2]))
            self.entrada.definir(self.entrada.preto, luma, self.entrada.gamma)
        self.conta_gotas = ""
        self.tela.ferramenta = "navegar"
        self._pintar_amostras()
        self._marcar()

    def _pintar_amostras(self) -> None:
        self._cor_botao(self.amostra_knockout, self.ajustes.knockout, "Vazado")
        self._cor_botao(self.amostra_camisa, self.ajustes.shirt, "Camiseta")
        if hasattr(self, "cor_fundo"):
            self.cor_fundo.setIcon(self._icone_troca_cor(self.ajustes.shirt))
            self.cor_fundo.setIconSize(QSize(20, 20))

    def _cor_botao(self, botao: QPushButton, cor: tuple, titulo: str) -> None:
        vermelho, verde, azul = (int(v) for v in cor)
        botao.setText(f"{titulo}  {vermelho:02X}{verde:02X}{azul:02X}")
        botao.setStyleSheet(
            f"background: rgb({vermelho},{verde},{azul}); color: {'#111' if (vermelho+verde+azul) > 380 else '#fff'};"
            "border-radius: 6px; padding: 6px;"
        )

    def _armar_pincel(self, ligado: bool) -> None:
        if ligado:
            self.varinha.setChecked(False)
            self.tela.ferramenta = "pincel"
            self.tela.raio_pincel = int(self.raio.value())
        elif self.tela.ferramenta == "pincel":
            self.tela.ferramenta = "navegar"

    def _armar_varinha(self, ligado: bool) -> None:
        if ligado:
            self.pincel.setChecked(False)
            self.tela.ferramenta = "varinha"
        elif self.tela.ferramenta == "varinha":
            self.tela.ferramenta = "navegar"

    def _atualizar_raio(self, valor: int) -> None:
        self.tela.raio_pincel = int(valor)

    def _garantir_mascaras(self) -> None:
        assert self.imagem is not None
        forma = self.imagem.shape[:2]
        if self.restaurar is None or self.restaurar.shape != forma:
            self.restaurar = np.zeros(forma, dtype=bool)
        if self.remover is None or self.remover.shape != forma:
            self.remover = np.zeros(forma, dtype=bool)

    def _pintar(self, x: int, y: int) -> None:
        if self.imagem is None:
            return
        self._garantir_mascaras()
        raio = int(self.raio.value())
        altura, largura = self.restaurar.shape
        y0, y1 = max(0, y - raio), min(altura, y + raio + 1)
        x0, x1 = max(0, x - raio), min(largura, x + raio + 1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        disco = (yy - y) ** 2 + (xx - x) ** 2 <= raio ** 2
        self.restaurar[y0:y1, x0:x1][disco] = True
        self.remover[y0:y1, x0:x1][disco] = False
        self._marcar()

    def _varinha(self, x: int, y: int) -> None:
        if self.imagem is None:
            return
        self._garantir_mascaras()
        cor = self.imagem[y, x, 0:3].astype(np.float32)
        diferenca = self.imagem[..., 0:3].astype(np.float32) - cor
        distancia = np.sqrt(np.sum(diferenca * diferenca, axis=-1))
        escolha = distancia <= float(self.tolerancia.value())
        self.remover[escolha] = True
        self.restaurar[escolha] = False
        self._marcar()

    def _atualizar_raio_tela(self) -> None:
        self.tela.raio_pincel = int(self.raio.value())
