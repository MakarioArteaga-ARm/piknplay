/* Consentimiento de cookies.
 *
 * Regla de la casa: el banner solo existe si hay algo que consentir. Con
 * ga4Id vacío, este archivo no pinta nada ni guarda nada — un aviso que pide
 * permiso para nada no es cumplimiento, es decoración, y además entrena a la
 * gente a darle «aceptar» sin leer.
 *
 * Cuando se configura la medición, la analítica se carga SOLO después del sí
 * explícito. Nunca antes, y «no, gracias» la bloquea de verdad.
 */

const CONFIG = window.PiknPlayConfig || {};
const GA4_ID = (CONFIG.ga4Id || '').trim();

// Para poder revisar el aviso sin encender la medición: ?cookies=demo
const MODO_PRUEBA = new URLSearchParams(location.search).get('cookies') === 'demo';
const HAY_QUE_CONSENTIR = Boolean(GA4_ID) || MODO_PRUEBA;

const CLAVE = 'consentimiento_piknplay';
// Versión del aviso bajo la que se dio el consentimiento: si el aviso cambia,
// se sabe con cuál decidió el visitante. El registro vive en el localStorage
// de SU navegador, así que sirve para respetar su decisión en visitas
// siguientes, no como prueba frente a terceros.
const VERSION = '2026-09';

const leer = () => {
  try {
    const crudo = localStorage.getItem(CLAVE);
    if (!crudo) return null;
    const dato = JSON.parse(crudo);
    return dato && dato.estado ? dato : null;
  } catch (error) {
    console.warn('No se pudo leer el consentimiento.', error);
    return null;
  }
};

const guardar = (estado) => {
  const registro = { estado, medicion: estado === 'aceptado', fecha: new Date().toISOString(), version: VERSION };
  try {
    localStorage.setItem(CLAVE, JSON.stringify(registro));
  } catch (error) {
    console.warn('No se pudo guardar el consentimiento.', error);
  }
  return registro;
};

const aceptoMedicion = () => leer()?.medicion === true;

// Se expone siempre, aunque no haya banner, para que el enlace del pie no
// lance nunca.
window.PiknPlayCookies = { abrirPreferencias: () => false, estado: leer, version: VERSION };

if (HAY_QUE_CONSENTIR) {
  // Interruptor oficial de GA4: si el visitante revoca después de haber
  // aceptado en esta misma visita, el script ya está cargado y bloquear la
  // carga no basta. Esto lo deja mudo sin recargar la página.
  const aplicarOptOut = () => {
    if (GA4_ID) window[`ga-disable-${GA4_ID}`] = !aceptoMedicion();
  };
  aplicarOptOut();

  let cargado = false;
  const cargarGA4 = () => {
    if (cargado || !GA4_ID || !aceptoMedicion()) return;
    cargado = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() {
      // biome-ignore lint/complexity/noArguments: gtag requiere el objeto arguments
      window.dataLayer.push(arguments);
    };
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID);
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`;
    document.head.appendChild(tag);
  };

  // El banner se inyecta desde aquí y no se copia en cada HTML: son cuatro
  // páginas y cuatro copias se desincronizan solas.
  const hoja = document.createElement('div');
  hoja.className = 'cookie-hoja';
  hoja.setAttribute('role', 'dialog');
  hoja.setAttribute('aria-labelledby', 'cookie-titulo');
  hoja.setAttribute('aria-describedby', 'cookie-texto');
  hoja.innerHTML = `
    <div class="cookie-card">
      <h2 id="cookie-titulo">¿Nos dejas medir las visitas?</h2>
      <p id="cookie-texto">
        El sitio no necesita cookies para funcionar. Solo nos gustaría saber cuánta
        gente entra y qué mira, con Google Analytics. Es voluntario y puedes cambiar
        de opinión cuando quieras.
      </p>
      <div class="cookie-acciones">
        <button type="button" class="btn btn-menta" data-cookie="rechazado">No, gracias</button>
        <button type="button" class="btn btn-primary" data-cookie="aceptado">Aceptar</button>
      </div>
      <p class="cookie-enlaces"><a href="/aviso-de-privacidad">Aviso de privacidad</a></p>
    </div>`;
  document.body.appendChild(hoja);

  const mostrar = () => hoja.classList.add('visible');
  const ocultar = () => hoja.classList.remove('visible');

  for (const boton of hoja.querySelectorAll('[data-cookie]')) {
    boton.addEventListener('click', () => {
      guardar(boton.dataset.cookie);
      aplicarOptOut();
      ocultar();
      cargarGA4();
    });
  }

  window.PiknPlayCookies.abrirPreferencias = () => {
    mostrar();
    return true;
  };

  // El enlace del pie solo tiene sentido si hay algo que gestionar.
  for (const enlace of document.querySelectorAll('[data-preferencias-cookies]')) {
    enlace.hidden = false;
    enlace.addEventListener('click', (evento) => {
      evento.preventDefault();
      window.PiknPlayCookies.abrirPreferencias();
    });
  }

  if (!leer()) {
    mostrar();
  } else if (aceptoMedicion()) {
    // Ya había aceptado: cargar cuando el navegador esté ocioso, para no
    // competir con el render inicial.
    (window.requestIdleCallback || ((cb) => setTimeout(cb, 2000)))(cargarGA4);
  }
}
