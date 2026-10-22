"""Gera o ícone ADNY com o símbolo de retículas do site (sem dependências pagas)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SIZE = 1024
im = Image.new("RGBA", (SIZE, SIZE), (19, 20, 24, 255))
draw = ImageDraw.Draw(im)
draw.rounded_rectangle((30, 30, 994, 994), radius=194, outline=(195, 170, 105), width=17)

# A progressão das nove retículas reproduz a marca de site/assets/mark.svg.
for row in range(3):
    for col in range(3):
        radius = (20, 30, 40)[min(row + col, 2)] * 2
        cx, cy = 282 + col * 230, 175 + row * 160
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(232, 220, 186))

fonts = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
font_path = next((path for path in fonts if path.exists()), None)
if not font_path:
    raise FileNotFoundError("Fonte necessária para gerar o ícone ADNY")
font = ImageFont.truetype(str(font_path), 195)
label = "ADNY"
bounds = draw.textbbox((0, 0), label, font=font)
width = bounds[2] - bounds[0]
draw.text(((SIZE-width)/2, 686), label, font=font, fill=(255, 255, 255), stroke_width=0)

im.save(ROOT / "adny-icon.png")
im.save(ROOT / "adny.ico", format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
