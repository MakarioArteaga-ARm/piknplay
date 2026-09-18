/* Arma el preview de un solo archivo a partir de las fuentes del repo.
 * Una sola fuente de verdad: index.html + css/src/*.css. Este script solo
 * los empaqueta (CSS embebido, sin <head>) para poder publicar el preview
 * sin servidor. NO edites el archivo de salida: se regenera. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const out = process.argv[2];
if (!out) {
  console.error('Uso: node scripts/build/bundle-preview.mjs <archivo-de-salida.html>');
  process.exit(1);
}

const TITULO = 'PiknPlay Playground'; // nombre corto: es el que ve la galería
// Las etiquetas de fuentes salen del propio index.html: si ahí se agrega
// una familia, el preview la hereda sin tocar este archivo.

const leer = (p) => fs.readFile(path.join(rootDir, p), 'utf8');

const html = await leer('index.html');
const FUENTES = (html.match(/<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>/g) || []).join('\n');
const cuerpo = html.match(/<body>([\s\S]*)<\/body>/);
if (!cuerpo) throw new Error('No encontré <body> en index.html');

const [base, movil, escritorio] = await Promise.all([
  leer('css/src/base.css'),
  leer('css/src/mobile.css'),
  leer('css/src/desktop.css'),
]);

const estilos = [
  base,
  `@media (max-width: 900px) {\n${movil}\n}`,
  `@media (min-width: 901px) {\n${escritorio}\n}`,
].join('\n\n');

const salida = `<title>${TITULO}</title>
${FUENTES}

<style>
${estilos}
</style>
${cuerpo[1]}`;

await fs.writeFile(out, salida, 'utf8');
console.log(`${out} — ${(salida.length / 1024).toFixed(0)} KB`);
