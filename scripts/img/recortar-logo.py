"""Recorta el logotipo original en sus piezas, para poder animarlo letra a letra.

    python3 scripts/img/recortar-logo.py

Antes la portada recreaba el logotipo con una tipografía parecida (Fredoka).
Parecida no es igual: la 'a' y la 'y' se notaban distintas del original. Esto
lo resuelve de raíz — las piezas SON el original, recortado.

Separa por manchas de tinta conectadas y no por cortes verticales: las cajas
de las letras se traslapan (la cola de la 'y' pasa por debajo de la 'a'), así
que un corte recto se llevaría pedazo de la vecina. Cada pieza se recorta con
su propia máscara.

Salidas: images/logo/<pieza>.png y el bloque de geometría dentro de
css/src/base.css, entre los marcadores PIEZAS DEL LOGOTIPO.
"""

import json
import pathlib
from collections import deque

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / 'images' / 'logo.png'
DESTINO = RAIZ / 'images' / 'logo'
CSS = RAIZ / 'css' / 'src' / 'base.css'

UMBRAL = 60        # alfa a partir del cual se considera tinta
MINIMO = 250       # manchas más chicas son motas de antialias
CORTE_SUB = 285    # a partir de esta Y empieza la línea PLAYGROUND

# El orden es por posición horizontal. El logotipo no cambia, así que la
# correspondencia es fija y explícita en vez de adivinada.
PRINCIPALES = ['p1', 'i-punto', 'i', 'k', 'rayo1', 'n', 'rayo2', 'rayo3', 'p2', 'l', 'a', 'y']
SUBTITULO = ['sub-punto-izq', 'sub-p', 'sub-l', 'sub-a', 'sub-y', 'sub-g',
             'sub-r', 'sub-o', 'sub-u', 'sub-n', 'sub-d', 'sub-punto-der']


def manchas(alfa, W, H):
    px = alfa.load()
    visto = bytearray(W * H)
    fuera = []
    for y0 in range(H):
        for x0 in range(W):
            if visto[y0 * W + x0] or px[x0, y0] <= UMBRAL:
                continue
            q = deque([(x0, y0)])
            visto[y0 * W + x0] = 1
            pts = []
            minx = maxx = x0
            miny = maxy = y0
            while q:
                x, y = q.popleft()
                pts.append((x, y))
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and not visto[ny * W + nx] and px[nx, ny] > UMBRAL:
                            visto[ny * W + nx] = 1
                            q.append((nx, ny))
            fuera.append({'bbox': (minx, miny, maxx, maxy), 'pts': pts})
    return fuera


def main():
    im = Image.open(ORIGEN).convert('RGBA')
    W, H = im.size
    todas = manchas(im.getchannel('A'), W, H)
    grandes = [m for m in todas if len(m['pts']) >= MINIMO]
    # A qué fila pertenece cada mancha se decide ANTES de absorber las motas:
    # una mota de la fila de arriba puede estirar la caja de una letra del
    # subtítulo y mandarla a la fila equivocada.
    for g in grandes:
        g['sub'] = g['bbox'][1] >= CORTE_SUB
    motas = [m for m in todas if len(m['pts']) < MINIMO]

    # Las motas de antialias se pegan a la mancha grande más cercana para que
    # no se pierda ningún pixel del dibujo original.
    for mota in motas:
        mx = (mota['bbox'][0] + mota['bbox'][2]) / 2
        my = (mota['bbox'][1] + mota['bbox'][3]) / 2
        fila = [g for g in grandes if g['sub'] == (my >= CORTE_SUB)] or grandes
        cerca = min(fila, key=lambda g: (mx - (g['bbox'][0] + g['bbox'][2]) / 2) ** 2
                                        + (my - (g['bbox'][1] + g['bbox'][3]) / 2) ** 2)
        cerca['pts'].extend(mota['pts'])
        bx0, by0, bx1, by1 = cerca['bbox']
        mx0, my0, mx1, my1 = mota['bbox']
        cerca['bbox'] = (min(bx0, mx0), min(by0, my0), max(bx1, mx1), max(by1, my1))

    principales = sorted([m for m in grandes if not m['sub']], key=lambda m: m['bbox'][0])
    subtitulo = sorted([m for m in grandes if m['sub']], key=lambda m: m['bbox'][0])
    assert len(principales) == len(PRINCIPALES), f'esperaba {len(PRINCIPALES)}, hay {len(principales)}'
    assert len(subtitulo) == len(SUBTITULO), f'esperaba {len(SUBTITULO)}, hay {len(subtitulo)}'

    DESTINO.mkdir(parents=True, exist_ok=True)
    for viejo in DESTINO.glob('*.png'):
        viejo.unlink()

    reglas = []
    for nombre, m in list(zip(PRINCIPALES, principales)) + list(zip(SUBTITULO, subtitulo)):
        x0, y0, x1, y1 = m['bbox']
        w, h = x1 - x0 + 1, y1 - y0 + 1
        pieza = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        origen = im.load()
        destino = pieza.load()
        # Solo los pixeles de ESTA mancha: así la vecina no se cuela en el
        # recorte aunque sus cajas se traslapen.
        for (x, y) in m['pts']:
            destino[x - x0, y - y0] = origen[x, y]
        pieza.save(DESTINO / f'{nombre}.png')
        reglas.append(
            f'.pz-{nombre} {{ left: {x0 / W * 100:.3f}%; top: {y0 / H * 100:.3f}%; '
            f'width: {w / W * 100:.3f}%; height: {h / H * 100:.3f}%; '
            f'background-image: url(../images/logo/{nombre}.png); }}'
        )

    bloque = ('/* INICIO PIEZAS DEL LOGOTIPO — generado por\n'
              '   scripts/img/recortar-logo.py. No editar a mano. */\n'
              + '\n'.join(reglas)
              + '\n/* FIN PIEZAS DEL LOGOTIPO */')
    css = CSS.read_text(encoding='utf-8')
    ini = css.index('/* INICIO PIEZAS DEL LOGOTIPO')
    fin = css.index('/* FIN PIEZAS DEL LOGOTIPO */') + len('/* FIN PIEZAS DEL LOGOTIPO */')
    CSS.write_text(css[:ini] + bloque + css[fin:], encoding='utf-8')

    print(f'{len(reglas)} piezas · proporción del lienzo {W}/{H}')
    print(json.dumps({'ancho': W, 'alto': H}, ensure_ascii=False))


if __name__ == '__main__':
    main()
