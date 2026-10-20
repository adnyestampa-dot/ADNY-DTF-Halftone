"""Peças de interface reutilizáveis."""

from __future__ import annotations

import math

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget


class FaixaColorida(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(3)

    def paintEvent(self, _evento) -> None:
        pintor = QPainter(self)
        gradiente = QLinearGradient(0, 0, self.width(), 0)
        gradiente.setColorAt(0, QColor("#ff4fd8"))
        gradiente.setColorAt(1, QColor("#3d7eff"))
        pintor.fillRect(self.rect(), gradiente)


class Secao(QWidget):
    def __init__(self, titulo: str, corpo: QWidget) -> None:
        super().__init__()
        self.botao = QToolButton()
        self.botao.setText(titulo)
        self.botao.setCheckable(True)
        self.botao.setChecked(True)
        self.botao.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.botao.setArrowType(Qt.DownArrow)
        self.botao.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.corpo = corpo
        self.botao.toggled.connect(self._alternar)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)
        layout.addWidget(self.botao)
        layout.addWidget(corpo)

    def _alternar(self, aberta: bool) -> None:
        self.corpo.setVisible(aberta)
        self.botao.setArrowType(Qt.DownArrow if aberta else Qt.RightArrow)


class FaixaLevels(QWidget):
    """Controle de levels. Os números desenhados são os valores lidos pelo motor."""

    alterado = Signal()

    def __init__(self, com_gamma: bool = True, com_histograma: bool = True) -> None:
        super().__init__()
        self.com_gamma = com_gamma
        self.com_histograma = com_histograma
        self.preto = 0
        self.branco = 255
        self.gamma = 1.0
        self.histograma = np.zeros(256, dtype=np.float32)
        self._arraste: str | None = None
        self.setMinimumHeight(132 if com_histograma else 58)
        self.setMinimumWidth(240)

    def definir(self, preto: int, branco: int, gamma: float = 1.0) -> None:
        self.preto = int(np.clip(preto, 0, 255))
        self.branco = int(np.clip(branco, 0, 255))
        self.gamma = float(np.clip(gamma, 0.1, 3.0))
        self.update()

    def definir_histograma(self, valores: np.ndarray) -> None:
        self.histograma = np.asarray(valores, dtype=np.float32)
        self.update()

    def _trilho(self) -> tuple[int, int, int]:
        esquerda = 14
        direita = max(esquerda + 10, self.width() - 14)
        topo = 78 if self.com_histograma else 16
        return esquerda, direita, topo

    def _x(self, valor: int) -> float:
        esquerda, direita, _topo = self._trilho()
        return esquerda + (direita - esquerda) * (valor / 255.0)

    def _valor(self, x: float) -> int:
        esquerda, direita, _topo = self._trilho()
        proporcao = (x - esquerda) / max(1.0, direita - esquerda)
        return int(round(min(1.0, max(0.0, proporcao)) * 255))

    def _t_gamma(self) -> float:
        return min(1.0, max(0.0, 0.5 + math.log10(min(3.0, max(0.1, self.gamma)))))

    def _gamma(self, proporcao: float) -> float:
        return min(3.0, max(0.1, 10 ** (proporcao - 0.5)))

    def _x_gamma(self) -> float:
        origem = self._x(self.preto)
        fim = self._x(self.branco)
        return origem + (fim - origem) * self._t_gamma()

    def paintEvent(self, _evento) -> None:
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.com_histograma:
            area = QRectF(14, 4, max(10, self.width() - 28), 66)
            pintor.fillRect(area, QColor("#101114"))
            pico = float(self.histograma.max()) if self.histograma.size else 0.0
            if pico > 0:
                largura = area.width() / 256.0
                pintor.setPen(Qt.PenStyle.NoPen)
                pintor.setBrush(QColor("#8ea0b8"))
                for indice, valor in enumerate(self.histograma):
                    altura = (valor / pico) * (area.height() - 4)
                    pintor.drawRect(QRectF(area.left() + indice * largura, area.bottom() - altura, largura, altura))
        esquerda, direita, topo = self._trilho()
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor("#3a3e48"))
        pintor.drawRoundedRect(QRectF(esquerda, topo, direita - esquerda, 4), 2, 2)
        self._puxador(pintor, self._x(self.preto), topo + 2, QColor("#111111"), QColor("#f5f5f5"))
        self._puxador(pintor, self._x(self.branco), topo + 2, QColor("#f5f5f5"), QColor("#111111"))
        if self.com_gamma:
            self._puxador(pintor, self._x_gamma(), topo + 2, QColor("#8fb0ff"), QColor("#102044"), 5)
        pintor.setPen(QColor("#d5d8de"))
        base = topo + 22
        pintor.drawText(QRectF(0, base, self.width() / 3, 18), Qt.AlignmentFlag.AlignHCenter, str(self.preto))
        if self.com_gamma:
            gamma = f"{self.gamma:.2f}".rstrip("0").rstrip(".")
            pintor.drawText(QRectF(self.width() / 3, base, self.width() / 3, 18), Qt.AlignmentFlag.AlignHCenter, gamma)
        pintor.drawText(
            QRectF(2 * self.width() / 3, base, self.width() / 3, 18),
            Qt.AlignmentFlag.AlignHCenter,
            str(self.branco),
        )

    def _puxador(self, pintor: QPainter, x: float, y: float, fundo: QColor, borda: QColor, raio: int = 7) -> None:
        pintor.setBrush(fundo)
        pintor.setPen(QPen(borda, 1))
        pintor.drawEllipse(QPointF(x, y), raio, raio)

    def mousePressEvent(self, evento) -> None:
        x = evento.position().x()
        candidatos = [("preto", self._x(self.preto)), ("branco", self._x(self.branco))]
        if self.com_gamma:
            candidatos.append(("gamma", self._x_gamma()))
        nome, posicao = min(candidatos, key=lambda item: abs(item[1] - x))
        if abs(posicao - x) <= 16:
            self._arraste = nome
            self.mouseMoveEvent(evento)

    def mouseMoveEvent(self, evento) -> None:
        if not self._arraste or not (evento.buttons() & Qt.MouseButton.LeftButton):
            return
        x = float(evento.position().x())
        if self._arraste == "preto":
            self.preto = min(self._valor(x), self.branco)
        elif self._arraste == "branco":
            self.branco = max(self._valor(x), self.preto)
        else:
            origem = self._x(self.preto)
            fim = self._x(self.branco)
            proporcao = 0.5 if fim <= origem else (x - origem) / (fim - origem)
            self.gamma = self._gamma(min(1.0, max(0.0, proporcao)))
        self.update()
        self.alterado.emit()

    def mouseReleaseEvent(self, _evento) -> None:
        self._arraste = None


class LinhaControle(QWidget):
    def __init__(self, titulo: str, controle: QWidget) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(QLabel(titulo))
        layout.addWidget(controle)
