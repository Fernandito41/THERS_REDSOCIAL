// Validación de UX en el Frontend -- la validación de seguridad definitiva
// (formato de email, reglas de contraseña) pertenece al Backend
// (API_CONTRACT.md §9, ítem 2: todavía PENDIENTE DE APROBACIÓN allí).
export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

// `username` todavía no existe como columna en `users` (DATABASE_ARCHITECTURE.md
// §4.B lo registra como candidato de Perfil, sin ratificar) ni lo acepta
// POST /api/register -- esta regla es solo UX para el campo visual nuevo del
// formulario de registro, no un contrato validado por Backend.
export function isValidUsername(value) {
  return /^[a-zA-Z0-9_]{3,20}$/.test(value.trim());
}

// `phone` tampoco existe en el contrato actual -- validación laxa (7 a 15
// dígitos, ignorando espacios/guiones) solo para detectar errores obvios de
// tipeo en el campo visual, no una regla de formato internacional real.
export function isValidPhone(value) {
  const digitsOnly = value.replace(/[^0-9]/g, "");
  return digitsOnly.length >= 7 && digitsOnly.length <= 15;
}
