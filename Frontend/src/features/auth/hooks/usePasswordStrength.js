const REQUIREMENTS = [
  { id: "length", label: "Al menos 8 caracteres", test: (v) => v.length >= 8 },
  { id: "uppercase", label: "Una letra mayúscula", test: (v) => /[A-Z]/.test(v) },
  { id: "lowercase", label: "Una letra minúscula", test: (v) => /[a-z]/.test(v) },
  { id: "number", label: "Un número", test: (v) => /[0-9]/.test(v) },
  { id: "special", label: "Un carácter especial (!@#$%...)", test: (v) => /[^A-Za-z0-9]/.test(v) },
];

const LEVELS = ["Muy débil", "Débil", "Media", "Fuerte", "Muy fuerte"];

// Lógica pura de fortaleza de contraseña, compartida por el componente
// PasswordStrength en Register y Reset Password (Fase 5 -- no duplicar
// lógica entre formularios). Es UX únicamente: la validación de seguridad
// definitiva pertenece al Backend.
export function usePasswordStrength(password) {
  const value = password || "";
  const requirements = REQUIREMENTS.map((req) => ({ ...req, met: req.test(value) }));
  const score = value ? requirements.filter((r) => r.met).length : 0;
  const levelIndex = value ? Math.max(0, Math.min(score - 1, LEVELS.length - 1)) : -1;

  return {
    requirements,
    score,
    percent: (score / REQUIREMENTS.length) * 100,
    levelIndex,
    level: levelIndex >= 0 ? LEVELS[levelIndex] : null,
  };
}
