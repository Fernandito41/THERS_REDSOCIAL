// Ids estables (sin texto embebido) -- PasswordStrength.jsx traduce cada
// requisito y cada nivel vía shared/i18n (auth.passwordStrength.*), así esta
// lógica pura se mantiene independiente del idioma seleccionado.
const REQUIREMENTS = [
  { id: "length", test: (v) => v.length >= 8 },
  { id: "uppercase", test: (v) => /[A-Z]/.test(v) },
  { id: "lowercase", test: (v) => /[a-z]/.test(v) },
  { id: "number", test: (v) => /[0-9]/.test(v) },
  { id: "special", test: (v) => /[^A-Za-z0-9]/.test(v) },
];

const LEVEL_COUNT = 5;

// Lógica pura de fortaleza de contraseña, compartida por el componente
// PasswordStrength en Register y Reset Password (Fase 5 -- no duplicar
// lógica entre formularios). Es UX únicamente: la validación de seguridad
// definitiva pertenece al Backend.
export function usePasswordStrength(password) {
  const value = password || "";
  const requirements = REQUIREMENTS.map((req) => ({ ...req, met: req.test(value) }));
  const score = value ? requirements.filter((r) => r.met).length : 0;
  const levelIndex = value ? Math.max(0, Math.min(score - 1, LEVEL_COUNT - 1)) : -1;

  return {
    requirements,
    score,
    percent: (score / REQUIREMENTS.length) * 100,
    levelIndex,
  };
}
