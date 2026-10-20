"""Palco da arte: vistas, zoom, recorte e ferramentas."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from app.engines.image_engine import px_para_unidade


def para_pixmap(rgba: np.ndarray) -> QPixmap:
    arr = np.ascontiguousarray(rgba)
    altura, largura, _canais = arr.shape
    imagem = QImage(arr.data, largura, altura, largura * 4, QImage.Format.Format_RGBA8888).copy()
    return QPixmap.fromImage(imagem)


class Tela(QWidget):
    abrir_pedido = Signal()
    zoom_mudou = Signal(int)
    amostra = Signal(int, int)
    pincel = Signal(int, int)
    varinha = Signal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setMouseTracking(True)
        self.modo = "original"
        self.esquerda: QPixmap | None = None
        self.direita: QPixmap | None = None
        self.tamanho: tuple[int, int] | None = None
        self.ajustar = True
        self.escala = 1.0
        self.pan = QPointF(0, 0)
        self.divisao = 0.5
        self.ferramenta = "navegar"
        self.recorte: QRect | None = None
        self.unidade = "in"
        self.raio_pincel = 24
        self._arraste: str | None = None
        self._origem = QPointF()
        self._recorte_inicial: QRect | None = None
        self._pan_inicial = QPointF()
        self.setMinimumSize(640, 420)

    def definir_imagens(self, modo: str, esquerda: np.ndarray | None, direita: np.ndarray | None = None) -> None:
        self.modo = modo
        if esquerda is None:
            self.esquerda = None
            self.direita = None
            self.tamanho = None
        else:
            self.esquerda = para_pixmap(esquerda)
            self.direita = para_pixmap(direita) if direita is not None else None
            self.tamanho = (esquerda.shape[1], esquerda.shape[0])
        self.update()
        self.zoom_mudou.emit(self.percentual())

    def percentual(self) -> int:
        return int(round(self._escala_atual() * 100))

    def ajustar_tela(self) -> None:
        self.ajustar = True
        self.update()
        self.zoom_mudou.emit(self.percentual())

    def zoom_real(self) -> None:
        self.definir_zoom(100)

    def definir_zoom(self, percentual: int) -> None:
        if not self.tamanho:
            return
        rect = self._destino()
        antiga = self._escala_atual()
        centro = QPointF(self.width() / 2, self.height() / 2)
        ix = (centro.x() - rect.x()) / antiga
        iy = (centro.y() - rect.y()) / antiga
        self.ajustar = False
        self.escala = max(0.05, min(4.0, percentual / 100.0))
        self.pan = QPointF(centro.x() - ix * self.escala, centro.y() - iy * self.escala)
        self.update()
        self.zoom_mudou.emit(self.percentual())

    def iniciar_recorte(self, rect: QRect) -> None:
        self.recorte = QRect(rect)
        self.ferramenta = "recorte"
        self.update()

    def _escala_atual(self) -> float:
        if not self.tamanho:
            return 1.0
        if not self.ajustar:
            return self.escala
        largura, altura = self.tamanho
        return max(0.01, min((self.width() - 56) / largura, (self.height() - 56) / altura))

    def _destino(self) -> QRectF:
        if not self.tamanho:
            return QRectF()
        largura, altura = self.tamanho
        escala = self._escala_atual()
        w, h = largura * escala, altura * escala
        if self.ajustar:
            return QRectF((self.width() - w) / 2, (self.height() - h) / 2, w, h)
        return QRectF(self.pan.x(), self.pan.y(), w, h)

    def _para_imagem(self, posicao: QPointF) -> tuple[int, int] | None:
        if not self.tamanho:
            return None
        rect = self._destino()
        if not rect.contains(posicao):
            return None
        x = int((posicao.x() - rect.x()) / self._escala_atual())
        y = int((posicao.y() - rect.y()) / self._escala_atual())
        largura, altura = self.tamanho
        return min(max(0, x), largura - 1), min(max(0, y), altura - 1)

    def paintEvent(self, _evento) -> None:
        pintor = QPainter(self)
        pintor.fillRect(self.rect(), QColor("#d5d6db"))
        if self.esquerda is None or not self.tamanho:
            pintor.setPen(QColor("#2a2c31"))
            pintor.setFont(QFont("Segoe UI", 18))
            pintor.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Click or drag artwork")
            return
        rect = self._destino()
        if self.modo == "split" and self.direita is not None:
            corte = rect.x() + rect.width() * self.divisao
            pintor.setClipRect(QRectF(rect.x(), rect.y(), corte - rect.x(), rect.height()))
            pintor.drawPixmap(rect, self.esquerda, QRectF(self.esquerda.rect()))
            pintor.setClipRect(QRectF(corte, rect.y(), rect.right() - corte, rect.height()))
            pintor.drawPixmap(rect, self.direita, QRectF(self.direita.rect()))
            pintor.setClipping(False)
            pintor.setPen(QPen(QColor("#f7f7f7"), 2))
            pintor.drawLine(int(corte), int(rect.top()), int(corte), int(rect.bottom()))
            pintor.setBrush(QColor("#1c1e22"))
            pintor.drawEllipse(QPointF(corte, rect.center().y()), 12, 12)
        else:
            pixmap = self.direita if self.modo != "original" and self.direita is not None else self.esquerda
            pintor.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
        if self.ferramenta == "recorte" and self.recorte is not None:
            self._desenhar_recorte(pintor, rect)
        if self.ferramenta == "pincel":
            pintor.setPen(QPen(QColor("#ffffff"), 1))
            pintor.setBrush(Qt.BrushStyle.NoBrush)

    def _desenhar_recorte(self, pintor: QPainter, destino: QRectF) -> None:
        assert self.recorte is not None
        escala = self._escala_atual()
        tela = QRectF(
            destino.x() + self.recorte.x() * escala,
            destino.y() + self.recorte.y() * escala,
            self.recorte.width() * escala,
            self.recorte.height() * escala,
        )
        sombra = QColor(0, 0, 0, 110)
        pintor.fillRect(QRectF(destino.x(), destino.y(), destino.width(), tela.top() - destino.top()), sombra)
        pintor.fillRect(QRectF(destino.x(), tela.bottom(), destino.width(), destino.bottom() - tela.bottom()), sombra)
        pintor.fillRect(QRectF(destino.x(), tela.top(), tela.left() - destino.left(), tela.height()), sombra)
        pintor.fillRect(QRectF(tela.right(), tela.top(), destino.right() - tela.right(), tela.height()), sombra)
        pintor.setPen(QPen(QColor("#ffffff"), 1))
        pintor.setBrush(Qt.BrushStyle.NoBrush)
        pintor.drawRect(tela)
        for ponto in (tela.topLeft(), tela.topRight(), tela.bottomLeft(), tela.bottomRight()):
            pintor.fillRect(QRectF(ponto.x() - 4, ponto.y() - 4, 8, 8), QColor("#ffffff"))
        texto = self._texto_recorte()
        pintor.setPen(QColor("#111111"))
        pintor.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        pintor.drawText(self.rect().adjusted(0, 14, -16, 0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, texto)

    def _texto_recorte(self) -> str:
        assert self.recorte is not None
        largura = px_para_unidade(self.recorte.width(), self.unidade)
        altura = px_para_unidade(self.recorte.height(), self.unidade)
        return f"{largura:.2f} × {altura:.2f} {self.unidade}    {self.recorte.width()} × {self.recorte.height()} px"

    def wheelEvent(self, evento) -> None:
        if not self.tamanho:
            return
        self.definir_zoom(self.percentual() + (10 if evento.angleDelta().y() > 0 else -10))

    def mousePressEvent(self, evento) -> None:
        if self.tamanho is None and evento.button() == Qt.MouseButton.LeftButton:
            self.abrir_pedido.emit()
            return
        if self.tamanho is None:
            return
        posicao = evento.position()
        if self.modo == "split" and self._perto_da_divisao(posicao):
            self._arraste = "divisao"
            return
        if self.ferramenta == "recorte":
            self._arraste = self._alca(posicao)
            self._origem = posicao
            self._recorte_inicial = QRect(self.recorte) if self.recorte else None
            return
        ponto = self._para_imagem(posicao)
        if ponto is None:
            return
        if self.ferramenta == "conta-gotas":
            self.amostra.emit(*ponto)
            return
        if self.ferramenta == "varinha" and evento.button() == Qt.MouseButton.LeftButton:
            self.varinha.emit(*ponto)
            return
        if self.ferramenta == "pincel" and evento.button() == Qt.MouseButton.LeftButton:
            self._arraste = "pincel"
            self.pincel.emit(*ponto)
            return
        if evento.button() == Qt.MouseButton.LeftButton:
            if self.ajustar:
                rect = self._destino()
                self.escala = self._escala_atual()
                self.pan = rect.topLeft()
                self.ajustar = False
            self._arraste = "pan"
            self._origem = posicao
            self._pan_inicial = QPointF(self.pan)

    def mouseMoveEvent(self, evento) -> None:
        if not self._arraste:
            return
        posicao = evento.position()
        if self._arraste == "divisao":
            rect = self._destino()
            if rect.width() > 0:
                self.divisao = min(0.95, max(0.05, (posicao.x() - rect.x()) / rect.width()))
                self.update()
            return
        if self._arraste == "pan":
            self.pan = self._pan_inicial + (posicao - self._origem)
            self.update()
            return
        if self._arraste == "pincel":
            ponto = self._para_imagem(posicao)
            if ponto:
                self.pincel.emit(*ponto)
            return
        if self.ferramenta == "recorte" and self._recorte_inicial is not None and self.tamanho:
            self._mover_recorte(posicao)

    def mouseReleaseEvent(self, _evento) -> None:
        self._arraste = None

    def _perto_da_divisao(self, posicao: QPointF) -> bool:
        rect = self._destino()
        corte = rect.x() + rect.width() * self.divisao
        return abs(posicao.x() - corte) <= 12 and rect.top() <= posicao.y() <= rect.bottom()

    def _alca(self, posicao: QPointF) -> str | None:
        if self.recorte is None:
            return None
        tela = self._recorte_na_tela()
        pontos = {
            "tl": tela.topLeft(),
            "tr": tela.topRight(),
            "bl": tela.bottomLeft(),
            "br": tela.bottomRight(),
        }
        for nome, ponto in pontos.items():
            if abs(posicao.x() - ponto.x()) <= 12 and abs(posicao.y() - ponto.y()) <= 12:
                return nome
        if tela.contains(posicao):
            return "mover"
        return None

    def _recorte_na_tela(self) -> QRectF:
        assert self.recorte is not None
        destino = self._destino()
        escala = self._escala_atual()
        return QRectF(
            destino.x() + self.recorte.x() * escala,
            destino.y() + self.recorte.y() * escala,
            self.recorte.width() * escala,
            self.recorte.height() * escala,
        )

    def _mover_recorte(self, posicao: QPointF) -> None:
        assert self._recorte_inicial is not None and self.tamanho
        escala = max(self._escala_atual(), 0.01)
        dx = int(round((posicao.x() - self._origem.x()) / escala))
        dy = int(round((posicao.y() - self._origem.y()) / escala))
        rect = QRect(self._recorte_inicial)
        largura, altura = self.tamanho
        if self._arraste == "mover":
            rect.translate(dx, dy)
        elif self._arraste == "tl":
            rect.setTopLeft(rect.topLeft() + QPoint(dx, dy))
        elif self._arraste == "tr":
            rect.setTopRight(rect.topRight() + QPoint(dx, dy))
        elif self._arraste == "bl":
            rect.setBottomLeft(rect.bottomLeft() + QPoint(dx, dy))
        elif self._arraste == "br":
            rect.setBottomRight(rect.bottomRight() + QPoint(dx, dy))
        rect = rect.normalized()
        rect.setWidth(max(8, rect.width()))
        rect.setHeight(max(8, rect.height()))
        if rect.left() < 0:
            rect.moveLeft(0)
        if rect.top() < 0:
            rect.moveTop(0)
        if rect.right() > largura:
            rect.moveRight(largura)
        if rect.bottom() > altura:
            rect.moveBottom(altura)
        self.recorte = rect
        self.update()
