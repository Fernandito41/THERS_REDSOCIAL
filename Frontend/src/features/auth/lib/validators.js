// Validación de UX en el Frontend -- la validación de seguridad definitiva
// (formato de email, reglas de contraseña) pertenece al Backend
// (API_CONTRACT.md §9, ítem 2: todavía PENDIENTE DE APROBACIÓN allí).
export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}
