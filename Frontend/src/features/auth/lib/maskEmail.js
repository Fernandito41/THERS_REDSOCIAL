// Enmascara la parte local de un email para mostrarlo en pantalla sin
// exponerlo completo (VerifyResetCode.jsx, ADR-010-password-reset-otp-flow.md
// §Fase 4 de la tarea) -- "diego@gmail.com" -> "d*****@gmail.com". Puramente
// de presentación: el email real sigue viajando completo en cada request al
// backend (router state, nunca en la URL).
export function maskEmail(email) {
  const [local, domain] = email.split("@");
  if (!local || !domain) return email;
  if (local.length === 1) return `${local}*@${domain}`;

  const maskedLength = Math.min(local.length - 1, 5);
  return `${local[0]}${"*".repeat(maskedLength)}@${domain}`;
}
