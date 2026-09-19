"""Genera el juego de iconos del sitio a partir de la marca.

    python3 scripts/img/generar-iconos.py

Salidas: images/favicon.ico (16/32/48), images/apple-touch-icon.png (180),
images/icon-192.png, images/icon-512.png.

El wordmark completo no sirve de favicon: es una pieza ancha y a 16px se
vuelve una mancha. El icono es la P inicial en blanco sobre un cuadrado
redondeado con un degradado en diagonal de los seis colores de la marca.

El orden de las paradas no es decorativo. Las claras —menta, cielo, ámbar—
van a las esquinas y las saturadas —uva, rosa, naranja— a la banda central,
que es justo donde cae la P: sobre esas tres el blanco se lee, sobre ámbar
no. Y el degradado abre en verde y azul, colores que la paleta de Instagram
no usa, para que el parecido sea con la técnica y no con su combinación.

La P va en Fredoka, la misma con la que estuvo recreado el logotipo.
"""

import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[2]
FUENTE_TTF = RAIZ / 'scripts' / 'og' / '.fonts' / 'fredoka.ttf'
FUENTE_URL = 'https://fonts.gstatic.com/s/fredoka/v17/X7nP4b87HvSqjb_WIi2yDCRwoQ_k7367_B-i2yQag0-mac3OLyXMFg.ttf'
IMAGENES = RAIZ / 'images'

AMBAR, MENTA, NARANJA = (242, 161, 30), (79, 189, 138), (244, 120, 58)
ROSA, CIELO, UVA = (232, 67, 127), (90, 174, 228), (139, 111, 212)
BLANCO = (255, 255, 255)

# Paradas del degradado, de una esquina a la otra. Claras afuera, saturadas
# en el centro: ahí es donde se apoya la P.
PARADAS = [(0.0, MENTA), (0.30, CIELO), (0.55, UVA), (0.74, ROSA), (0.90, NARANJA), (1.0, AMBAR)]

LADO = 512  # se dibuja grande una vez y se reduce, para que no se vea sucio


def base():
    if not FUENTE_TTF.exists():
        FUENTE_TTF.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['curl', '-sSfL', FUENTE_URL, '-o', str(FUENTE_TTF)], check=True)

    # Degradado en diagonal: la posición de cada pixel sobre el eje que va de
    # la esquina superior izquierda a la inferior derecha.
    fondo = Image.new('RGB', (LADO, LADO))
    px = fondo.load()
    for y in range(LADO):
        for x in range(LADO):
            t = (x + y) / (2 * (LADO - 1))
            for i in range(len(PARADAS) - 1):
                t0, c0 = PARADAS[i]
                t1, c1 = PARADAS[i + 1]
                if t0 <= t <= t1:
                    k = (t - t0) / (t1 - t0)
                    px[x, y] = tuple(round(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                    break

    # El cuadrado redondeado se recorta con máscara para que el borde quede
    # suave; dibujarlo relleno encima del degradado lo taparía.
    mascara = Image.new('L', (LADO, LADO), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, LADO - 1, LADO - 1],
                                              radius=round(LADO * .22), fill=255)
    icono = Image.new('RGBA', (LADO, LADO), (0, 0, 0, 0))
    icono.paste(fondo, (0, 0), mascara)
    d = ImageDraw.Draw(icono)

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
            fondo = Image.new('RGB', (lado, lado), UVA)
            fondo.paste(img, (0, 0), img)
            img = fondo
        img.save(IMAGENES / nombre)
        print(f'  images/{nombre} · {lado}x{lado}')

    ico = IMAGENES / 'favicon.ico'
    icono.save(ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f'  images/favicon.ico · 16/32/48 · {ico.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
