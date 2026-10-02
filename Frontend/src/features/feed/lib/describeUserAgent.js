// Resume un `User-Agent` para mostrarlo en la lista de sesiones
// (ADR-025-session-registry.md).
//
// El servidor lo guarda **crudo** a propósito: no tiene una base de datos de
// user agents y adivinar ahí produciría etiquetas equivocadas que quedarían
// persistidas. Este resumen vive en el Frontend, donde es solo presentación y
// se puede corregir sin tocar datos.
//
// Reglas deliberadamente conservadoras: si no se reconoce el navegador o el
// sistema, se devuelve el texto original recortado. **Un texto raro es más útil
// que una etiqueta equivocada** — alguien puede reconocer su propio user agent,
// pero no puede reconocer un "Chrome en Windows" que en realidad era su Edge.

// El orden importa: Edge y Opera incluyen "Chrome" en su UA, y Chrome incluye
// "Safari". Se evalúa de más específico a más genérico.
const BROWSERS = [
  [/\bEdg(?:e|A|iOS)?\//i, "Edge"],
  [/\bOPR\/|\bOpera\//i, "Opera"],
  [/\bFirefox\/|\bFxiOS\//i, "Firefox"],
  [/\bChrome\/|\bCriOS\//i, "Chrome"],
  [/\bSafari\//i, "Safari"],
];

const PLATFORMS = [
  [/\bAndroid\b/i, "Android"],
  [/\biPhone\b/i, "iPhone"],
  [/\biPad\b/i, "iPad"],
  [/\bWindows\b/i, "Windows"],
  [/\bMac OS X\b|\bMacintosh\b/i, "macOS"],
  [/\bLinux\b/i, "Linux"],
];

const MAX_FALLBACK_LENGTH = 48;

function matchFirst(candidates, value) {
  for (const [pattern, label] of candidates) {
    if (pattern.test(value)) return label;
  }
  return null;
}

export function describeUserAgent(userAgent) {
  if (!userAgent || typeof userAgent !== "string") {
    // El header puede faltar: un cliente no está obligado a mandarlo.
    return "Dispositivo desconocido";
  }

  const browser = matchFirst(BROWSERS, userAgent);
  const platform = matchFirst(PLATFORMS, userAgent);

  if (browser && platform) return `${browser} en ${platform}`;
  if (browser) return browser;
  if (platform) return platform;

  // Ni navegador ni sistema reconocidos (un cliente de API, un bot, un UA
  // personalizado): se muestra tal cual, recortado.
  const trimmed = userAgent.trim();
  return trimmed.length > MAX_FALLBACK_LENGTH
    ? `${trimmed.slice(0, MAX_FALLBACK_LENGTH)}…`
    : trimmed;
}
