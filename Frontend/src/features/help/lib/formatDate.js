const MONTH_NAMES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

// Formatea un ISO "YYYY-MM-DD" (formato de `updatedAt` en data/articles.js)
// como "25 de agosto de 2026" -- sin agregar una dependencia de fechas nueva.
export function formatHelpDate(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  return `${day} de ${MONTH_NAMES[month - 1]} de ${year}`;
}
