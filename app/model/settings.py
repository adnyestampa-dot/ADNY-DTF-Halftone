"""Controles visíveis. O valor guardado aqui é o valor processado."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

SHAPES = ("circle", "ellipse", "diamond", "square", "line")
SHAPE_LABELS = {
    "circle": "Redondo",
    "ellipse": "Elipse",
    "diamond": "Losango",
    "square": "Quadrado",
    "line": "Linha",
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
    dpi_y: float | None = None
    dpi_informado: bool = False

    def validate(self) -> None:
        erros: list[str] = []
        lpi = float(self.lpi)
        if lpi < 20 or lpi > 45:
            erros.append(f"LPI {lpi:g} está fora de 20–45.")
        if self.dot_shape not in SHAPES:
            erros.append(f"Forma de ponto desconhecida: {self.dot_shape}.")
        if int(self.choke_px) not in (0, 1, 2):
            erros.append("A redução da base branca só aceita 0, 1 ou 2 px.")
        if not 0 <= int(self.mask_threshold) <= 255:
            erros.append("O limiar da máscara precisa ficar entre 0 e 255.")
        nomes = {
            "input_black": "O preto de entrada",
            "input_white": "O branco de entrada",
            "output_black": "O preto de saída",
            "output_white": "O branco de saída",
        }
        for nome in nomes:
            valor = int(getattr(self, nome))
            if not 0 <= valor <= 255:
                erros.append(f"{nomes[nome]} precisa ficar entre 0 e 255.")
        gamma = float(self.gamma)
        if gamma < 0.1 or gamma > 3:
            erros.append("A gama precisa ficar entre 0,10 e 3,00.")
        angulo = float(self.angle)
        if angulo < 0 or angulo > 90:
            erros.append("O ângulo precisa estar entre 0 e 90.")
        if not 0 <= int(self.cleanup) <= 100:
            erros.append("A limpeza precisa ficar entre 0 e 100 px.")
        if self.white_mode not in ("layer", "mask", "spot"):
            erros.append("Modo da base branca inválido.")
        if self.dpi is not None and float(self.dpi) <= 0:
            erros.append("O DPI do arquivo precisa ser maior que zero.")
        if self.dpi_y is not None and float(self.dpi_y) <= 0:
            erros.append("O DPI vertical do arquivo precisa ser maior que zero.")
        if erros:
            raise ValueError(" ".join(erros))

    def to_dict(self) -> dict:
        dados = asdict(self)
        dados["knockout"] = [int(v) for v in self.knockout]
        dados["shirt"] = [int(v) for v in self.shirt]
        dados["lpi"] = float(self.lpi)
        dados["angle"] = float(self.angle)
        dados["gamma"] = float(self.gamma)
        if self.dpi is not None:
            dados["dpi"] = float(self.dpi)
        if self.dpi_y is not None:
            dados["dpi_y"] = float(self.dpi_y)
        dados["dpi_informado"] = bool(self.dpi_informado)
        return dados

    @classmethod
    def from_dict(cls, dados: dict) -> "Settings":
        conhecidos = {campo.name for campo in fields(cls)}
        limpo = {chave: valor for chave, valor in dados.items() if chave in conhecidos}
        if "knockout" in limpo:
            limpo["knockout"] = tuple(int(v) for v in limpo["knockout"])
        if "shirt" in limpo:
            limpo["shirt"] = tuple(int(v) for v in limpo["shirt"])
        if "dpi_informado" not in dados and dados.get("dpi"):
            limpo["dpi_informado"] = True
        objeto = cls(**limpo)
        objeto.validate()
        return objeto
