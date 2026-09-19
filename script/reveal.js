/* Aparición al scroll. Solo corre si el guard del <head> puso .js-reveal, es
 * decir si hay IntersectionObserver y el visitante no pidió menos movimiento.
 * Si no está, no hay nada que hacer: todo ya se ve. */
const docEl = document.documentElement;

if (docEl.classList.contains('js-reveal') && 'IntersectionObserver' in window) {
  // Avisar al guard de que su red de seguridad de 2.5 s ya no hace falta.
  docEl.dataset.revealReady = '1';

  // Escalonado corto: los bloques que entran juntos no caen de golpe, pero
  // tampoco es una cascada de plantilla. Tres pasos de 70 ms y se acabó.
  const MAX_PASOS = 3;

  const observador = new IntersectionObserver(
    (entradas) => {
      let paso = 0;
      entradas
        .filter((entrada) => entrada.isIntersecting)
        // El orden de `entradas` no está garantizado; ordenar por posición
        // hace que la aparición baje por la página en vez de saltar.
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        .forEach((entrada) => {
          const n = Math.min(paso, MAX_PASOS);
          paso += 1;
          entrada.target.classList.add('is-revealed');
          if (n > 0) {
            entrada.target.classList.add(`reveal-d${n}`);
          }
          // Una sola vez. Re-animar al volver a subir marea en scroll largo.
          observador.unobserve(entrada.target);
        });
    },
    { rootMargin: '0px 0px -12% 0px', threshold: 0.05 },
  );

  for (const el of document.querySelectorAll('.animate-on-scroll')) {
    observador.observe(el);
  }
}
