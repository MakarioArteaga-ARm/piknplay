"""Genera el juego de iconos del sitio a partir de la marca.

    python3 scripts/img/generar-iconos.py

Salidas: images/favicon.ico (16/32/48), images/apple-touch-icon.png (180),
images/icon-192.png, images/icon-512.png.

El wordmark completo no sirve de favicon: es una pieza ancha y a 16px se
vuelve una mancha. El icono es la P inicial en blanco sobre un cuadrado
redondeado rosa — el rosa es el color de acento del sitio y el mismo del
theme-color, y con blanco encima se lee en la pestaña, que es lo único que
tiene que hacer. La P va en Fredoka, la misma tipografía con la que está
recreado el logotipo en la portada.
"""

import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[2]
FUENTE_TTF = RAIZ / 'scripts' / 'og' / '.fonts' / 'fredoka.ttf'
FUENTE_URL = 'https://fonts.gstatic.com/s/fredoka/v17/X7nP4b87HvSqjb_WIi2yDCRwoQ_k7367_B-i2yQag0-mac3OLyXMFg.ttf'
IMAGENES = RAIZ / 'images'

ROSA = (232, 67, 127)
BLANCO = (255, 255, 255)
LADO = 512  # se dibuja grande una vez y se reduce, para que no se vea sucio


def base():
    if not FUENTE_TTF.exists():
        FUENTE_TTF.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['curl', '-sSfL', FUENTE_URL, '-o', str(FUENTE_TTF)], check=True)

    icono = Image.new('RGBA', (LADO, LADO), (0, 0, 0, 0))
    d = ImageDraw.Draw(icono)
    d.rounded_rectangle([0, 0, LADO - 1, LADO - 1], radius=round(LADO * .22), fill=(*ROSA, 255))

    f = ImageFont.truetype(str(FUENTE_TTF), round(LADO * .68))
    izq, arriba, der, abajo = d.textbbox((0, 0), 'P', font=f)
    d.text(((LADO - (der - izq)) / 2 - izq, (LADO - (abajo - arriba)) / 2 - arriba),
           'P', font=f, fill=(*BLANCO, 255))
    return icono


def main():
    icono = base()
    IMAGENES.mkdir(exist_ok=True)

    for nombre, lado in [('icon-512.png', 512), ('icon-192.png', 192), ('apple-touch-icon.png', 180)]:
        # El de Apple no admite transparencia: se aplana sobre el propio rosa.
        img = icono.resize((lado, lado), Image.LANCZOS)
        if nombre.startswith('apple'):
            fondo = Image.new('RGB', (lado, lado), ROSA)
            fondo.paste(img, (0, 0), img)
            img = fondo
        img.save(IMAGENES / nombre)
        print(f'  images/{nombre} · {lado}x{lado}')

    ico = IMAGENES / 'favicon.ico'
    icono.save(ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f'  images/favicon.ico · 16/32/48 · {ico.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
