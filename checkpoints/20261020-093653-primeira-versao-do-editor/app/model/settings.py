"""Controles visíveis. O valor guardado aqui é o valor processado."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

SHAPES = ("circle", "ellipse", "diamond", "square", "line")
SHAPE_LABELS = {
    "circle": "Round",
    "ellipse": "Ellipse",
    "diamond": "Diamond",
    "square": "Square",
    "line": "Line",
}
LABEL_TO_SHAPE = {label: key for key, label in SHAPE_LABELS.items()}


@dataclass
class Settings:
    lpi: float = 30.0
    angle: float = 22.5
    dot_shape: str = "circle"
    halftone_enabled: bool = True
    dpi: int = 300
    knockout: tuple = (0, 0, 0)
    shirt: tuple = (0, 0, 0)
    link_shirt: bool = True
    shirt_preview: bool = False
    mask_threshold: int = 24
    input_black: int = 0
    input_white: int = 255
    gamma: float = 1.0
    output_black: int = 0
    output_white: int = 255
    hue: float = 0.0
    saturation: float = 0.0
    lightness: float = 0.0
    cleanup: int = 0
    underbase: bool = False
    choke_px: int = 0
    white_mode: str = "layer"

    def validate(self) -> None:
        erros: list[str] = []
        lpi = float(self.lpi)
        if lpi < 20 or lpi > 45:
            erros.append(f"LPI {lpi:g} está fora de 20–45.")
        if self.dot_shape not in SHAPES:
            erros.append(f"Forma de ponto desconhecida: {self.dot_shape}.")
        if int(self.choke_px) not in (0, 1, 2):
            erros.append("O choke da base branca só aceita 0, 1 ou 2 px.")
        if not 0 <= int(self.mask_threshold) <= 255:
            erros.append("Mask threshold precisa estar entre 0 e 255.")
        for nome in ("input_black", "input_white", "output_black", "output_white"):
            valor = int(getattr(self, nome))
            if not 0 <= valor <= 255:
                erros.append(f"{nome} fora de 0–255.")
        gamma = float(self.gamma)
        if gamma < 0.1 or gamma > 3:
            erros.append("Gamma precisa estar entre 0.10 e 3.00.")
        angulo = float(self.angle)
        if angulo < 0 or angulo > 90:
            erros.append("O ângulo precisa estar entre 0 e 90.")
        if not 0 <= int(self.cleanup) <= 100:
            erros.append("Cleanup precisa estar entre 0 e 100 px.")
        if self.white_mode not in ("layer", "mask", "spot"):
            erros.append("Modo da base branca inválido.")
        if int(self.dpi) != 300:
            erros.append("O DPI de trabalho confirmado é 300.")
        if erros:
            raise ValueError(" ".join(erros))

    def to_dict(self) -> dict:
        dados = asdict(self)
        dados["knockout"] = [int(v) for v in self.knockout]
        dados["shirt"] = [int(v) for v in self.shirt]
        dados["lpi"] = float(self.lpi)
        dados["angle"] = float(self.angle)
        dados["gamma"] = float(self.gamma)
        return dados

    @classmethod
    def from_dict(cls, dados: dict) -> "Settings":
        conhecidos = {campo.name for campo in fields(cls)}
        limpo = {chave: valor for chave, valor in dados.items() if chave in conhecidos}
        if "knockout" in limpo:
            limpo["knockout"] = tuple(int(v) for v in limpo["knockout"])
        if "shirt" in limpo:
            limpo["shirt"] = tuple(int(v) for v in limpo["shirt"])
        objeto = cls(**limpo)
        objeto.validate()
        return objeto
