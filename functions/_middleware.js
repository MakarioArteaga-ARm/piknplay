// Cierra los archivos internos que Cloudflare despliega por estar en el
// repositorio pero que no forman parte del sitio.
//
// Por qué un middleware y no reglas en _redirects: en Pages, _redirects solo
// se aplica a rutas que NO existen como archivo. Los archivos internos SÍ
// existen en el despliegue, así que ganan y las reglas nunca se evalúan.
// Las Functions, en cambio, corren antes que los archivos estáticos.
// (Lección tomada del repo de armlaboral.com, donde esto se verificó en vivo:
// con reglas en _redirects los archivos internos seguían dando 200.)
//
// La lista es de DENEGACIÓN, no de permiso: si mañana se añade una página o
// una imagen, se sirve sin tocar nada. Solo hay que añadir aquí lo nuevo que
// sea herramental.
const BLOQUEADAS = [
  /^\/scripts\//,
  /^\/css\/src\//,
  /^\/\.claude\//,
  /^\/\.github\//,
  /^\/(package(-lock)?\.json|biome\.json|README\.md|\.gitignore)$/,
];

const noEncontrado = () =>
  new Response('Not Found', {
    status: 404,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store, max-age=0, must-revalidate',
      'X-Robots-Tag': 'noindex, nofollow',
    },
  });

export const onRequest = (context) => {
  const { pathname } = new URL(context.request.url);
  if (BLOQUEADAS.some((patron) => patron.test(pathname))) {
    return noEncontrado();
  }
  return context.next();
};
