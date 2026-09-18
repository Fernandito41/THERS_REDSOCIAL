// Preferencias de Configuración — almacenamiento LOCAL por cuenta.
//
// POR QUÉ LOCAL: no existe ningún endpoint de preferencias. El backend solo
// expone auth, perfil, posts, likes, comentarios, follows y notificaciones
// (API_CONTRACT.md §4), y `PATCH /api/users/me` acepta únicamente
// name/username/phone/country_code/birth_date (ADR-003). Inventar un contrato
// de preferencias sería exactamente lo que prohíben CLAUDE.md §14 y el
// archivo maestro §9.4.
//
// La alternativa —dejar los controles sin persistir— haría que un ajuste se
// perdiera al recargar, que es peor y además engañoso. Se sigue el mismo
// criterio que `profileStorage.js`, que ya existía en este repositorio para
// bio/ubicación/portada: guardar en el navegador y **decirlo en pantalla**.
//
// LÍMITE IMPORTANTE, declarado en la interfaz: una preferencia local NO es
// una regla aplicada. Ocultar un control no protege datos (archivo maestro
// §8.10). Privacidad, bloqueo, 2FA, sesiones, pagos y tokens NO se modelan
// aquí: son decisiones de servidor y se muestran como no disponibles.

const KEY_PREFIX = "thers_settings_";

function storageKey(username) {
  return `${KEY_PREFIX}${username}`;
}

export function loadSettings(username) {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKey(username)));
    return raw && typeof raw === "object" ? raw : {};
  } catch {
    return {};
  }
}

export function saveSetting(username, key, value) {
  try {
    const current = loadSettings(username);
    localStorage.setItem(storageKey(username), JSON.stringify({ ...current, [key]: value }));
  } catch {
    // Cuota llena o almacenamiento bloqueado: el valor sigue en memoria
    // durante la sesión y la pantalla no se rompe.
  }
}

export function clearSettings(username) {
  try {
    localStorage.removeItem(storageKey(username));
  } catch {
    // Igual que arriba.
  }
}
