"""Genera la tarjeta Open Graph: images/og.jpg, 1200x630.

Es la imagen que aparece cuando alguien pega el link en WhatsApp, Facebook o
X. Se genera, no se dibuja a mano, para que cuando cambie la marca o el
mensaje baste con volver a correr esto.

    python3 scripts/og/generar-og.py

Por qué Python y no Node como el resto del repo: ARm hace sus tarjetas con
Playwright + sharp (renderiza una plantilla HTML y la fotografía), que son
cientos de megas de dependencias. Aquí la tarjeta es una composición fija y
Pillow —que ya está en el sistema— la arma sin instalar nada.

Las tipografías se descargan a scripts/og/.fonts/ la primera vez. No se
versionan ni se despliegan: son insumo del generador, no del sitio.
"""

import pathlib
import random
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[2]
FUENTES_DIR = RAIZ / 'scripts' / 'og' / '.fonts'
SALIDA = RAIZ / 'images' / 'og.jpg'

W, H = 1200, 630

AMBAR, MENTA, NARANJA = (242, 161, 30), (79, 189, 138), (244, 120, 58)
ROSA, CIELO, UVA = (232, 67, 127), (90, 174, 228), (139, 111, 212)
TINTA, APAGADO = (43, 43, 54), (94, 94, 112)
PALETA = [AMBAR, MENTA, CIELO, ROSA, UVA, NARANJA]

FUENTES = {
    'fredoka': 'https://fonts.gstatic.com/s/fredoka/v17/X7nP4b87HvSqjb_WIi2yDCRwoQ_k7367_B-i2yQag0-mac3OLyXMFg.ttf',
    'nunito': 'https://fonts.gstatic.com/s/nunito/v32/XRXI3I6Li01BKofiOc5wtlZ2di8HDFwmRTM.ttf',
}


def fuente(nombre, tam):
    FUENTES_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FUENTES_DIR / f'{nombre}.ttf'
    if not ruta.exists():
        print(f'  bajando {nombre}…')
        # curl y no urllib: este Python no trae el bundle de certificados y
        # falla el handshake con fonts.gstatic.com.
        subprocess.run(['curl', '-sSfL', FUENTES[nombre], '-o', str(ruta)], check=True)
    return ImageFont.truetype(str(ruta), tam)


def fondo():
    """Base cálida en degradado vertical + seis manchas de color desenfocadas,
    el mismo gesto que el fondo del sitio."""
    paradas = [(0.0, (255, 248, 236)), (0.32, (253, 243, 248)), (0.62, (239, 248, 253)),
               (0.82, (241, 251, 245)), (1.0, (255, 250, 240))]
    base = Image.new('RGB', (1, H))
    px = base.load()
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(paradas) - 1):
            t0, c0 = paradas[i]
            t1, c1 = paradas[i + 1]
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0)
                px[0, y] = tuple(round(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
    lienzo = base.resize((W, H), Image.BICUBIC)

    manchas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(manchas)
    for (cx, cy, r, color, alfa) in [
        (60, -40, 460, CIELO, 120), (1150, 20, 420, AMBAR, 115),
        (900, 250, 380, UVA, 70), (40, 380, 400, ROSA, 70),
        (1080, 600, 420, MENTA, 95), (150, 660, 380, NARANJA, 80),
    ]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alfa))
    manchas = manchas.filter(ImageFilter.GaussianBlur(120))
    lienzo = Image.alpha_composite(lienzo.convert('RGBA'), manchas)
    return lienzo


def confeti(lienzo, n=70):
    """Mismo confeti del sitio: círculos y barritas en los seis colores."""
    random.seed(5)
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for i in range(n):
        color = PALETA[i % len(PALETA)]
        # Se quedan en las orillas: el centro lo ocupan el logo y el texto.
        x = random.choice([random.randint(10, 250), random.randint(950, 1190)]) \
            if random.random() < .62 else random.randint(10, 1190)
        y = random.randint(8, H - 24)
        if i % 5 == 0:
            w, h = random.randint(7, 10), random.randint(20, 30)
            pieza = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(pieza).rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 2,
                                                    fill=(*color, 150))
            pieza = pieza.rotate(random.randint(-40, 40), expand=True, resample=Image.BICUBIC)
            capa.alpha_composite(pieza, (x, y))
        else:
            r = random.randint(5, 11)
            ImageDraw.Draw(capa).ellipse([x, y, x + r * 2, y + r * 2], fill=(*color, 150))
    return Image.alpha_composite(lienzo, capa)


def centrar(d, texto, f, y, color):
    izq, arriba, der, abajo = d.textbbox((0, 0), texto, font=f)
    d.text(((W - (der - izq)) / 2 - izq, y), texto, font=f, fill=color)
    return abajo - arriba


def main():
    lienzo = confeti(fondo())

    # El logotipo va tal cual, no recreado: a 300px en un chat lo único que
    # tiene que leerse es la marca.
    logo = Image.open(RAIZ / 'images' / 'logo.png').convert('RGBA')
    ancho = 660
    logo = logo.resize((ancho, round(logo.height * ancho / logo.width)), Image.LANCZOS)
    lienzo.alpha_composite(logo, ((W - ancho) // 2, 120))

    d = ImageDraw.Draw(lienzo)
    centrar(d, 'Juegos y fiestas infantiles', fuente('fredoka', 58), 372, TINTA)
    centrar(d, 'Plaza 3 Arcos · Tampico, Tamaulipas', fuente('nunito', 32), 460, APAGADO)

    # La franja de los seis colores, como la del encabezado.
    franja = 12
    for i, color in enumerate(PALETA):
        x0 = round(W * i / len(PALETA))
        x1 = round(W * (i + 1) / len(PALETA))
        d.rectangle([x0, H - franja, x1, H], fill=color)

    SALIDA.parent.mkdir(exist_ok=True)
    lienzo.convert('RGB').save(SALIDA, 'JPEG', quality=88, optimize=True, progressive=True)
    print(f'{SALIDA.relative_to(RAIZ)} · {W}x{H} · {SALIDA.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
