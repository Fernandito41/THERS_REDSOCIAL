/**
 * Estado de sesión de la app móvil.
 *
 * Equivalente de `Frontend/src/features/auth/context/AuthContext.jsx`, con dos
 * diferencias deliberadas:
 * - los tokens (access y refresh, ADR-017) van a SecureStore, no a
 *   `localStorage` (THERS_PROMPT §7);
 * - el `user` NO se cachea en disco: se restaura siempre desde
 *   `GET /api/users/me`, que es la fuente de verdad (`API_CONTRACT.md` §4.2).
 *
 * Contexto/estado mínimo a propósito: el encargo (§5) pide no agregar otra
 * biblioteca de estado global sin necesidad demostrada. Zustand/Redux entran
 * si aparece un problema real, no por anticipación.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

import { ApiError, request, revokeSessionOnServer, waitForRefresh } from '@shared/lib/api';
import { clearSession, getRefreshToken, getToken, setSession } from '@shared/lib/session';

import type { LoginResponse, User } from '../types';

type AuthState = {
  user: User | null;
  /** `true` mientras se restaura la sesión al arrancar: evita parpadear el login. */
  isRestoring: boolean;
  /**
   * `true` si hay una sesión guardada pero no se pudo comprobar (sin red, o el
   * servidor no respondió). La sesión NO está cerrada: la app debe ofrecer
   * reintentar, no mandar al login.
   */
  restoreFailed: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  /** Vuelve a pedir `GET /api/users/me`. Devuelve `false` si la sesión ya no vale. */
  refreshUser: () => Promise<boolean>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isRestoring, setIsRestoring] = useState(true);
  const [restoreFailed, setRestoreFailed] = useState(false);

  /**
   * Única lectura de la identidad actual. `request()` ya renueva el access
   * token por su cuenta ante un `401` (ADR-017); si aún así llega un `401`, la
   * sesión de verdad terminó (refresh revocado, expirado o ausente) y se limpia:
   * quedarse con un `user` en memoria sin sesión produce pantallas que mienten.
   *
   * Cualquier OTRO fallo (sin red, timeout, `5xx`) **no** cierra la sesión: el
   * token puede seguir siendo válido y el usuario estar sin cobertura, o el
   * servidor caído un momento. Cerrar sesión ahí haría que perder señal
   * equivalga a un logout. Se marca `restoreFailed` para que la app ofrezca
   * reintentar en vez de mostrar el login.
   */
  const loadCurrentUser = useCallback(async (): Promise<boolean> => {
    try {
      // El backend envuelve al usuario: `{"user": {...}}` (API_CONTRACT.md §4.2),
      // igual que `login`. Guardar la respuesta cruda dejaba todos los campos en
      // `undefined` al restaurar la sesión.
      const { user: current } = await request<{ user: User }>('/users/me', {
        authenticated: true,
      });
      setUser(current);
      setRestoreFailed(false);
      return true;
    } catch (error) {
      if (error instanceof ApiError && error.isUnauthorized) {
        await clearSession();
        setUser(null);
        setRestoreFailed(false);
        return false;
      }
      setRestoreFailed(true);
      return false;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      // Hay sesión si existe cualquiera de los dos tokens: sin access pero con
      // refresh, `request()` lo recupera renovando.
      const hasSession = (await getToken()) !== null || (await getRefreshToken()) !== null;
      if (hasSession) await loadCurrentUser();
      if (!cancelled) setIsRestoring(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [loadCurrentUser]);

  const login = useCallback(async (email: string, password: string) => {
    // `.trim()` solo en el email, igual que el backend (`auth_routes.py`): un
    // espacio final de autocompletado hacía que `find_by_email()` no coincida.
    // La contraseña NUNCA se normaliza -- alteraría su valor real.
    const data = await request<LoginResponse>('/login', {
      method: 'POST',
      body: { email: email.trim(), password },
    });

    // Los tokens se persisten ANTES de publicar el user: si `setSession` falla,
    // no se deja la app "logueada" con una sesión que no sobrevive al cierre.
    await setSession({ accessToken: data.token, refreshToken: data.refresh_token });
    setRestoreFailed(false);
    setUser(data.user);
  }, []);

  const logout = useCallback(async () => {
    // ADR-017 §4.6: el logout limpia los DOS lados. Primero se espera a una
    // renovación en curso (si no, podría reescribir tokens justo después de
    // borrarlos), se revoca la sesión en el servidor (mejor esfuerzo: sin red
    // igual se cierra localmente) y por último se borra el almacenamiento.
    // El access token ya emitido sigue siendo válido hasta expirar (<= 15 min):
    // el backend no tiene lista de revocación de access tokens.
    await waitForRefresh();
    await revokeSessionOnServer();
    await clearSession();
    setUser(null);
    setRestoreFailed(false);
  }, []);

  const value = useMemo<AuthState>(
    () => ({ user, isRestoring, restoreFailed, login, logout, refreshUser: loadCurrentUser }),
    [user, isRestoring, restoreFailed, login, logout, loadCurrentUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  }
  return context;
}
