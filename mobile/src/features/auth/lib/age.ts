/**
 * Edad mínima y cálculo de edad por fecha COMPLETA.
 *
 * THERS es solo para personas de 18 años cumplidos o más (decisión de producto
 * del equipo, 2026-10-02; `ADR-034-minimum-age-18.md`). Este valor es el mismo
 * que `MIN_AGE_YEARS` del backend (`domain/auth/validators.py`) y de la web
 * (`Frontend/src/features/auth/lib/dateUtils.js`).
 *
 * Es la fecha que la persona DECLARA: no es una verificación documental. La
 * barrera real es la del servidor, que revalida; esto solo evita una ida y
 * vuelta por un error obvio y muestra el mensaje antes.
 */
export const MIN_AGE_YEARS = 18;

/** `true` si `iso` (`yyyy-mm-dd`) es una fecha real del calendario. */
export function isValidISODate(iso: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return false;
  const [year, month, day] = iso.split('-').map(Number);
  if (month < 1 || month > 12 || day < 1) return false;
  // `Date.UTC` + `getUTCDate` detecta días inexistentes (31 de abril, 29-feb en
  // año no bisiesto) sin depender de la zona horaria del teléfono.
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return (
    parsed.getUTCFullYear() === year &&
    parsed.getUTCMonth() === month - 1 &&
    parsed.getUTCDate() === day
  );
}

/**
 * Edad en años cumplidos a la fecha de `reference`. Compara año, mes y día: no
 * resta años a secas. Devuelve `null` si `iso` no es una fecha válida.
 *
 * Misma convención que el backend: quien nació un 29 de febrero cumple años el
 * 1 de marzo en un año no bisiesto.
 */
export function calculateAge(iso: string, reference: Date = new Date()): number | null {
  if (!isValidISODate(iso)) return null;
  const [year, month, day] = iso.split('-').map(Number);
  const refMonth = reference.getMonth() + 1;
  let age = reference.getFullYear() - year;
  const hadBirthday = refMonth > month || (refMonth === month && reference.getDate() >= day);
  if (!hadBirthday) age -= 1;
  return age;
}

/** `true` si la fecha es válida y la persona tiene `MIN_AGE_YEARS` o más. */
export function meetsMinimumAge(iso: string, reference: Date = new Date()): boolean {
  const age = calculateAge(iso, reference);
  return age !== null && age >= MIN_AGE_YEARS;
}

export const MIN_AGE_MESSAGE = `THERS es solo para personas de ${MIN_AGE_YEARS} años o más.`;
