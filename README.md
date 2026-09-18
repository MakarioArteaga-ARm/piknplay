# PiknPlay Playground — sitio web

Sitio de **Grupo PiknPlay, S.A.S.** (Plaza 3 Arcos, Tampico, Tamaulipas).
Destino: `https://www.piknplay.mx`.

Mismo contrato técnico que el repo de armlaboral.com: **HTML estático, sin
framework, sin paso de compilación en el despliegue.** Lo que está en el repo es
exactamente lo que se sirve.

## Arrancar

```bash
npm run dev     # servidor estático en http://localhost:4175
```

No hay `npm install` obligatorio para ver el sitio: el servidor de desarrollo
usa solo módulos de Node. Las dependencias son únicamente para el linter.

## Estructura

```
index.html              Portada
404.html                Página de error
css/src/*.css           FUENTE DE VERDAD del CSS — se edita aquí
css/*.css               Generados. NO editar a mano
images/logo.png         Logotipo original (favicon y Open Graph)
scripts/dev/            Servidor estático de desarrollo
scripts/build/          Empaquetador del preview de un archivo
_headers                Cabeceras de seguridad y caché (Cloudflare Pages)
_redirects              URLs limpias
functions/_middleware   Cierra los archivos internos en el despliegue
```

## Despliegue

Cloudflare Pages, conectado a este repo. **Sin paso de compilación**: el
despliegue publica lo que está commiteado.

| Ajuste | Valor |
|---|---|
| Framework preset | None |
| Build command | *(vacío)* |
| Build output directory | `/` |
| Production branch | `main` |

### Por qué existe `functions/_middleware.js`

Pages publica **todo** lo que está en el repo, incluidos `scripts/` y
`css/src/`. Bloquearlos desde `_redirects` no funciona: esas reglas solo se
aplican a rutas que **no** existen como archivo, y esos archivos sí existen en
el despliegue, así que ganan y la regla nunca se evalúa. Las Functions corren
antes que los archivos estáticos, por eso el bloqueo va ahí.

### El CSS va partido en tres

`base.css` carga siempre; `mobile.css` y `desktop.css` se cargan con atributo
`media` desde el HTML, así el navegador los descarga sin bloquear el render.
Se edita `css/src/` y se copia a `css/`. **Falta** `scripts/build/minify.mjs`,
que debe minificar `css/src/*.css → css/*.css` y escribir el cache-buster `?v=`
en el HTML a partir del hash del contenido; mientras tanto `css/` es copia
literal de `css/src/` y el `?v=` dice `dev`.

Esto importa porque `_headers` cachea `/css/*` como `immutable` por 365 días:
sin cache-buster, un cambio de CSS no le llega a quien ya visitó el sitio.

### El logotipo no es una imagen

En la portada el logotipo son **ocho letras de texto** (`.wordmark`), cada una
con su color, inclinación, tamaño y altura tomados del original, más el punto
de la i y los tres rayos como elementos aparte. Así cada pieza se anima por su
cuenta. El PNG sigue en `/images` para favicon y Open Graph.

La coreografía completa cuelga de una sola variable, `--t0` en `:root`: es el
momento en que arranca el logotipo, después de la ráfaga de confeti. Todos los
tiempos se miden contra ella.

### El preview de un archivo

```bash
npm run preview   # dist/preview.html
```

Toma `index.html` + `css/src/*.css` y los empaqueta en un HTML autocontenido
(CSS embebido, sin `<head>`), para publicarlo sin servidor. Es derivado: no se
edita a mano.

## Pendientes

- Tarifas, horarios y fotos del local — los tiene que dar el cliente.
- Autoalojar Baloo 2, Fredoka y Nunito en `/fonts`. Hoy van por Google Fonts y
  por eso `_headers` abre `style-src`/`font-src`; al autoalojarlas, las dos
  directivas vuelven a `'self'`.
- `scripts/build/minify.mjs` (minificado + cache-buster).
- Páginas de reglamento y aviso de privacidad (el pie ya enlaza a ambas).
- `sitemap.xml`, favicon e imagen de Open Graph.
