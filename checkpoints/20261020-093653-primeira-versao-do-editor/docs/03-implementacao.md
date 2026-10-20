# Implementação

A primeira versão está em Python, com PySide6 na interface e os motores em `app/engines`. O arquivo `iniciar.py` sobe o monitor e o editor.

O fluxo confirmado funciona: abrir PNG, JPG ou o .dtx deste clone, arrastar a arte, ver Original, Separation, Split View e Mask, ajustar retícula, levels, tamanho, recorte, camisa, HSL, cleanup e base branca, aplicar e exportar PNG. Save grava em `dados/projetos/projeto.dtx`.

A retícula aceita só 20–45 LPI. Fora disso o motor recusa o valor. O padrão é 30 LPI, 22,5° e Round. A saída zera o RGB onde o alfa é 0 e só grava alfa 0 ou 255.

Não entrou nesta versão: AI upscaler, gang sheet, o .dtx proprietário e a comparação com o aplicativo original.
