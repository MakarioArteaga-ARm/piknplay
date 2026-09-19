// --- CONFIGURACIÓN DEL SITIO DE PIKNPLAY ---
// Un solo lugar para los valores que se repiten o que se encienden y apagan.
window.PiknPlayConfig = {
  // WhatsApp (código de país de 2 dígitos + 10 dígitos).
  whatsapp: '528333890683',

  // Medición. MIENTRAS ESTÉ VACÍO el sitio no carga analítica y el banner de
  // cookies NO aparece: no hay nada que consentir. Al pegar aquí el ID de
  // Google Analytics 4 (G-XXXXXXXXXX) se encienden las dos cosas.
  //
  // OJO: encenderlo exige además abrir la CSP en _headers, o el navegador
  // bloqueará el script. Ver el README, sección «Medición y cookies».
  ga4Id: '',
};
