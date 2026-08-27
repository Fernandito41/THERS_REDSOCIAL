// Utilidades puras de fecha para el selector de fecha de nacimiento de
// Register.jsx -- sin dependencias externas (no se agregó ninguna librería
// de fechas nueva al proyecto para esto).

export const MONTH_NAMES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

// Semana en formato Lunes-a-Domingo (convención usada en el resto de LatAm/ES,
// y la misma que pidió el wireframe de la tarea).
export const WEEKDAY_LABELS = ["L", "M", "M", "J", "V", "S", "D"];

// THERS todavía no tiene una política de edad mínima ratificada en ningún
// documento oficial -- CLAUDE.md §15 confirma este hueco explícitamente. 13
// es un valor placeholder de UX (el mínimo más común entre redes sociales),
// centralizado en esta única constante para que sea trivial de ajustar
// cuando el equipo lo ratifique. Backend deberá aplicar la misma regla (o la
// que se decida) del lado del servidor -- este valor nunca es, por sí solo,
// la barrera real de la regla de negocio.
export const MIN_AGE_YEARS = 13;

function pad(value) {
  return String(value).padStart(2, "0");
}

export function daysInMonth(year, monthIndex) {
  return new Date(year, monthIndex + 1, 0).getDate();
}

// 0 = lunes ... 6 = domingo (Date.getDay() nativo es 0 = domingo).
function mondayFirstWeekday(year, monthIndex, day) {
  return (new Date(year, monthIndex, day).getDay() + 6) % 7;
}

export function toISODate(year, monthIndex, day) {
  return `${year}-${pad(monthIndex + 1)}-${pad(day)}`;
}

// Grilla de semanas (arrays de 7) para renderizar el calendario -- `null`
// representa una celda de relleno antes del día 1 o después del último día.
export function buildCalendarWeeks(year, monthIndex) {
  const totalDays = daysInMonth(year, monthIndex);
  const leadingBlanks = mondayFirstWeekday(year, monthIndex, 1);

  const cells = [
    ...Array(leadingBlanks).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ];
  while (cells.length % 7 !== 0) cells.push(null);

  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }
  return weeks;
}

export function isValidISODate(iso) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) return false;
  const [year, month, day] = iso.split("-").map(Number);
  if (month < 1 || month > 12) return false;
  return day >= 1 && day <= daysInMonth(year, month - 1);
}

// Formato "18 / Agosto / 2009" -- el mismo que pidió el wireframe de la tarea.
// `monthNames` es opcional (default = MONTH_NAMES en español) para que
// BirthDateField.jsx pueda pasar los nombres traducidos de shared/i18n sin
// que esta función deje de ser utilizable de forma independiente.
export function formatDisplayDate(iso, monthNames = MONTH_NAMES) {
  if (!isValidISODate(iso)) return "";
  const [year, month, day] = iso.split("-").map(Number);
  return `${day} / ${monthNames[month - 1]} / ${year}`;
}

export function calculateAge(iso, referenceDate = new Date()) {
  if (!isValidISODate(iso)) return null;
  const [year, month, day] = iso.split("-").map(Number);
  let age = referenceDate.getFullYear() - year;
  const hasHadBirthdayThisYear =
    referenceDate.getMonth() + 1 > month ||
    (referenceDate.getMonth() + 1 === month && referenceDate.getDate() >= day);
  if (!hasHadBirthdayThisYear) age -= 1;
  return age;
}
