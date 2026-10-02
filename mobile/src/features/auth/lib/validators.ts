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
