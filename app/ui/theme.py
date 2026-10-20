"""Aparência aproximada da miniatura pública. Os hexadecimais não foram extraídos do original."""

ESCURO = """
QMainWindow, QWidget { background: #121316; color: #f3f4f6; font-family: "Segoe UI"; font-size: 12px; }
QLabel#titulo { font-size: 16px; font-weight: 700; }
QLabel#sub { color: #a7adb8; font-size: 12px; }
QLabel#estado { color: #3ddc97; font-weight: 600; }
QLabel#dica { color: #9aa1ab; font-size: 11px; }
QLabel#medidas { color: #d5d8de; }
QFrame#cabecalho, QFrame#rodape, QFrame#lateral { background: #17181d; }
QFrame#lateral { border-right: 1px solid #2c2e35; }
QScrollArea { border: none; background: transparent; }
QToolButton { color: #f3f4f6; background: transparent; border: none; padding: 4px 8px; font-weight: 600; }
QToolButton::menu-indicator { image: none; }
QPushButton#vista { background: transparent; color: #c6cbd4; border: none; border-bottom: 2px solid transparent; padding: 8px 12px; border-radius: 0; }
QPushButton#vista:checked { color: white; border-bottom: 2px solid #6aa2ff; }
QFrame#fundoCamisa { background: #22242b; border: 1px solid #3c404a; border-radius: 8px; }
QFrame#fundoCamisa QCheckBox { color: #f3f4f6; spacing: 6px; }
QToolButton#trocaCor { background: transparent; border: none; padding: 0; }
QPushButton#primario { background: #2f6fed; color: white; border: none; border-radius: 8px; padding: 10px; font-weight: 700; }
QPushButton#primario:disabled { background: #343844; color: #8d939e; }
QPushButton#secundario, QPushButton#neutro { background: #2a2d36; color: #f3f4f6; border: 1px solid #3c404a; border-radius: 8px; padding: 8px; }
QPushButton#secundario:disabled { color: #8d939e; background: #23262e; }
QComboBox, QDoubleSpinBox, QSpinBox { background: #101114; color: #f3f4f6; border: 1px solid #343844; border-radius: 6px; padding: 4px 8px; min-height: 24px; }
QCheckBox { spacing: 8px; }
QSlider::groove:horizontal { height: 4px; background: #3a3e48; border-radius: 2px; }
QSlider::handle:horizontal { background: #f3f4f6; width: 14px; margin: -6px 0; border-radius: 7px; }
"""

CLARO = """
QMainWindow, QWidget { background: #f4f5f7; color: #1c1e22; font-family: "Segoe UI"; font-size: 12px; }
QLabel#titulo { font-size: 16px; font-weight: 700; }
QLabel#sub { color: #5c6370; font-size: 12px; }
QLabel#estado { color: #0f8a4b; font-weight: 600; }
QLabel#dica { color: #5c6370; font-size: 11px; }
QLabel#medidas { color: #1c1e22; }
QFrame#cabecalho, QFrame#rodape, QFrame#lateral { background: #ffffff; }
QFrame#lateral { border-right: 1px solid #d9dce3; }
QScrollArea { border: none; background: transparent; }
QToolButton { color: #1c1e22; background: transparent; border: none; padding: 4px 8px; font-weight: 600; }
QToolButton::menu-indicator { image: none; }
QPushButton#vista { background: transparent; color: #3d4450; border: none; border-bottom: 2px solid transparent; padding: 8px 12px; border-radius: 0; }
QPushButton#vista:checked { color: #123a86; border-bottom: 2px solid #2f6fed; }
QFrame#fundoCamisa { background: #f7f8fa; border: 1px solid #cfd3dc; border-radius: 8px; }
QFrame#fundoCamisa QCheckBox { color: #1c1e22; spacing: 6px; }
QToolButton#trocaCor { background: transparent; border: none; padding: 0; }
QPushButton#primario { background: #2f6fed; color: white; border: none; border-radius: 8px; padding: 10px; font-weight: 700; }
QPushButton#primario:disabled { background: #d5d8e0; color: #7b818c; }
QPushButton#secundario, QPushButton#neutro { background: #ffffff; color: #1c1e22; border: 1px solid #cfd3dc; border-radius: 8px; padding: 8px; }
QComboBox, QDoubleSpinBox, QSpinBox { background: #ffffff; color: #1c1e22; border: 1px solid #cfd3dc; border-radius: 6px; padding: 4px 8px; min-height: 24px; }
QCheckBox { spacing: 8px; }
QSlider::groove:horizontal { height: 4px; background: #d0d4dc; border-radius: 2px; }
QSlider::handle:horizontal { background: #2f6fed; width: 14px; margin: -6px 0; border-radius: 7px; }
"""
