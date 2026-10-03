/**
 * Validación de UX, portada de `Frontend/src/features/auth/lib/validators.js`.
 *
 * Es uno de los 33 módulos puros (sin DOM) que ADR-016 §2.2 identificó como
 * reutilizables: la lógica es idéntica, solo cambia el tipado.
 *
 * La validación DEFINITIVA es del backend (`domain/auth/validators.py`):
 * `is_valid_email` con la misma regex, `is_valid_password` con
 * `MIN_PASSWORD_LENGTH = 8`. Esto solo evita una ida y vuelta por un error de
 * tipeo obvio -- nunca sustituye al servidor, que revalida todo.
 */

export function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

/** Igual que `USERNAME_RE` del backend: 3 a 20 letras, números o guion bajo. */
export function isValidUsername(value: string): boolean {
  return /^[a-zA-Z0-9_]{3,20}$/.test(value.trim());
}

/** Igual que `is_valid_phone` del backend: 7 a 15 dígitos, ignorando separadores. */
export function isValidPhone(value: string): boolean {
  const digits = value.replace(/[^0-9]/g, '');
  return digits.length >= 7 && digits.length <= 15;
}

/** Igual que `COUNTRY_CODE_RE` del backend: `+` y de 1 a 4 dígitos, sin cero inicial. */
export function isValidCountryCode(value: string): boolean {
  return /^\+[1-9]\d{0,3}$/.test(value.trim());
}

/**
 * Mismo umbral que `MIN_PASSWORD_LENGTH` del backend (8, sin exigir mayúscula,
 * número ni símbolo). Es un placeholder de producto explícito y revisable
 * (`API_CONTRACT.md` v0.7), no una política de seguridad ratificada.
 *
 * No se endurece acá por iniciativa propia: si el cliente exigiera más que el
 * servidor, habría contraseñas válidas imposibles de usar desde la app.
 */
export const MIN_PASSWORD_LENGTH = 8;

export function isValidPassword(value: string): boolean {
  return value.length >= MIN_PASSWORD_LENGTH;
}
