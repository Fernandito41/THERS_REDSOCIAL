/**
 * Tipos del contrato HTTP, no del modelo de persistencia.
 *
 * Fuente única: `docs/architecture/API_CONTRACT.md` §5 ("Modelo de datos
 * expuesto por la API", v0.19). Si un campo no está ahí, no se tipa acá --
 * tipar un campo que el backend no expone crea la ilusión de un contrato que
 * no existe.
 *
 * Deliberadamente AUSENTES (y por qué):
 * - `password_hash` -- nunca cruza la frontera HTTP. `has_password` es un
 *   booleano derivado.
 * - `username_changed_at` -- existe en `users` pero es interno al cooldown de
 *   `username` (`ADR-003`); el contrato lo excluye a propósito.
 * - `avatar_url` / `bio` -- `API_CONTRACT.md` §5 los marca como **sin
 *   ratificar**. `ADR-015-profile-media.md` está en trabajo sin commitear; se
 *   agregarán acá el día que el contrato los publique, no por anticipación
 *   (`HB-001` §15.1).
 */

export type User = {
  id: string;
  username: string;
  email: string;
  name: string;
  /** Nullable desde v0.17: una cuenta creada con Google no los aporta. */
  phone: string | null;
  country_code: string | null;
  birth_date: string | null;
  followers_count: number;
  following_count: number;
  email_verified: boolean;
  /**
   * `false` cuando faltan `phone`/`country_code`/`birth_date` -- el caso de una
   * cuenta nacida de `POST /api/auth/google` (`ADR-012`). Se completa
   * reutilizando `PATCH /api/users/me`, sin endpoint nuevo.
   *
   * Esta primera entrega **no** implementa esa pantalla de onboarding; solo
   * refleja el estado. Queda para la fase de Google (ROADMAP fase 2).
   */
  profile_completed: boolean;
  has_password: boolean;
};

/** Sesión emitida: `POST /api/login`, `POST /api/auth/google` y `POST /api/2fa/verify`. */
export type SessionResponse = {
  token: string;
  /** Desde API_CONTRACT v0.21 (`ADR-017`). Opcional por tolerancia a un backend anterior. */
  refresh_token?: string;
  user: User;
};

/**
 * Segundo paso pendiente: la cuenta tiene 2FA (`ADR-026`). Esta respuesta **no
 * trae sesión**: ni `token` ni `user`. El `two_factor_token` es un token de
 * desafío de 5 minutos que no sirve en ningún endpoint protegido.
 */
export type TwoFactorChallenge = {
  two_factor_required: true;
  two_factor_token: string;
};

/** Respuesta de `POST /api/login`: una sesión o un desafío de 2FA (API_CONTRACT §4.1, §4.12). */
export type LoginResponse = SessionResponse | TwoFactorChallenge;

/** Respuesta de `POST /api/2fa/verify`: la sesión más el estado de los códigos de recuperación. */
export type TwoFactorVerifyResponse = SessionResponse & {
  used_recovery_code: boolean;
  recovery_codes_remaining: number;
};

export function isTwoFactorChallenge(response: LoginResponse): response is TwoFactorChallenge {
  return 'two_factor_required' in response && response.two_factor_required === true;
}

/** Respuesta de `POST /api/refresh` (API_CONTRACT §4.16). */
export type RefreshResponse = {
  token: string;
  refresh_token: string;
};
