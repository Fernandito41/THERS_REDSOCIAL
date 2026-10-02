/**
 * Almacenamiento de la sesión en el dispositivo.
 *
 * Contrato que implementa (THERS_PROMPT_CLAUDE_ANDROID.md §7, ADR-017 §4.5):
 * - Los tokens van en SecureStore -- cifrado en Android con claves gestionadas
 *   por Android Keystore. NUNCA en AsyncStorage, archivos planos, logs, URLs
 *   ni fixtures.
 * - Se guardan los DOS: el access token (15 min) y el refresh token (30 días,
 *   un solo uso, ADR-017). Guardar también el access es la decisión 2 de
 *   ADR-017 §7: así un arranque en frío intenta `GET /api/users/me` primero y
 *   solo renueva si hace falta, en vez de exigir red para abrir la app.
 * - SecureStore es para secretos pequeños. El objeto `user` NO se guarda acá:
 *   se vuelve a pedir a `GET /api/users/me`, que es la fuente de verdad
 *   (mismo criterio que `AuthContext.jsx` del Frontend, API_CONTRACT.md §4.2).
 * - Un error de lectura o borrado no puede dejar la app en un estado ambiguo:
 *   ante cualquier fallo se trata como "sin sesión", nunca como "sesión
 *   válida" (fail-closed).
 *
 * SecureStore no reemplaza los controles del servidor: una pantalla protegida
 * no es autorización. Cada petición lleva su `Authorization` y el backend
 * decide (`@jwt_required()`).
 */

import * as SecureStore from 'expo-secure-store';

const ACCESS_TOKEN_KEY = 'thers.access_token';
const REFRESH_TOKEN_KEY = 'thers.refresh_token';

async function readKey(key: string): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(key);
  } catch {
    // Almacenamiento no disponible o valor corrupto. Fail-closed: sin sesión.
    return null;
  }
}

/**
 * Lee el access token. Devuelve `null` tanto si no hay sesión como si la
 * lectura falla -- quien llama no debe distinguir esos casos.
 */
export function getToken(): Promise<string | null> {
  return readKey(ACCESS_TOKEN_KEY);
}

/** Lee el refresh token, con la misma semántica fail-closed. */
export function getRefreshToken(): Promise<string | null> {
  return readKey(REFRESH_TOKEN_KEY);
}

/**
 * Persiste la sesión. Si falla, propaga el error: el llamador debe saber que
 * la sesión no sobrevivirá al cierre de la app, en vez de creer que sí.
 *
 * Orden deliberado: primero el refresh, después el access. Si algo se corta
 * entre ambas escrituras, queda un refresh válido (la sesión se puede
 * recuperar) y nunca un access huérfano sin forma de renovarlo.
 *
 * `refreshToken` ausente borra el refresh guardado: así no sobrevive uno de una
 * sesión anterior junto a un access nuevo, que mezclaría usuarios.
 */
export async function setSession(session: {
  accessToken: string;
  refreshToken?: string | null;
}): Promise<void> {
  if (session.refreshToken) {
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, session.refreshToken);
  } else {
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
  }
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, session.accessToken);
}

/**
 * Borra ambos tokens. No lanza: un logout nunca debe quedar bloqueado porque el
 * almacenamiento falle -- el estado en memoria se limpia igual, y es el que
 * gobierna la navegación. Cada borrado es independiente: que falle uno no
 * impide intentar el otro.
 */
export async function clearSession(): Promise<void> {
  for (const key of [ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]) {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch {
      // Intencionalmente silencioso, ver nota de arriba.
    }
  }
}
