/* Servidor estático de desarrollo. Mismo patrón que armlaboral.com:
   sirve el repo tal cual se despliega, sin build ni framework. */
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..', '..');
const PORT = Number(process.env.PORT || 4173);
const HOST = process.env.HOST || '127.0.0.1';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
};

const sanitize = (urlPath) => {
  const decoded = decodeURIComponent(urlPath.split('?')[0].split('#')[0]);
  const normalized = path.posix.normalize(decoded);
  return normalized.includes('..') ? null : normalized;
};

const exists = async (p) => {
  try { await fs.access(p); return true; } catch { return false; }
};

async function resolveFile(urlPath) {
  if (urlPath === '/') return path.join(rootDir, 'index.html');
  const clean = sanitize(urlPath);
  if (!clean) return null;
  const direct = path.join(rootDir, clean);
  if (await exists(direct)) {
    const stat = await fs.stat(direct);
    if (stat.isDirectory()) {
      const idx = path.join(direct, 'index.html');
      return (await exists(idx)) ? idx : null;
    }
    return direct;
  }
  // URLs limpias sin .html, como en _redirects (/:splat.html -> /:splat).
  const asHtml = `${direct}.html`;
  return (await exists(asHtml)) ? asHtml : null;
}

http
  .createServer(async (req, res) => {
    const file = await resolveFile(new URL(req.url, `http://${HOST}`).pathname);
    if (!file) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('No encontrado');
      return;
    }
    const body = await fs.readFile(file);
    res.writeHead(200, {
      'Content-Type': MIME[path.extname(file)] || 'application/octet-stream',
      'Cache-Control': 'no-store',
    });
    res.end(body);
  })
  .listen(PORT, HOST, () => console.log(`PiknPlay dev → http://${HOST}:${PORT}`));
