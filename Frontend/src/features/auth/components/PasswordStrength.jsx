import { usePasswordStrength } from "../hooks/usePasswordStrength";

const BAR_COLORS = ["bg-ember-600", "bg-ember-500", "bg-warning-500", "bg-success-500", "bg-success-600"];
const TEXT_COLORS = ["text-ember-400", "text-ember-400", "text-warning-500", "text-success-500", "text-success-500"];

// Reutilizable entre Register y Reset Password (Fase 5). No depende del
// color como único indicador: también expone el nivel en texto y un
// checklist con símbolo ✓/○ por requisito (Fase 12 -- accesibilidad).
export default function PasswordStrength({ password }) {
  const { requirements, level, levelIndex, percent } = usePasswordStrength(password);

  if (!password) return null;

  return (
    <div className="mt-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-muted-dark">Seguridad de la contraseña</span>
        <span className={`text-xs font-semibold ${TEXT_COLORS[levelIndex]}`}>{level}</span>
      </div>

      <div
        className="h-1.5 w-full bg-line-dark rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={levelIndex + 1}
        aria-valuemin={0}
        aria-valuemax={5}
        aria-label={`Seguridad de la contraseña: ${level}`}
      >
        <div
          className={`h-full rounded-full transition-all duration-300 ${BAR_COLORS[levelIndex]}`}
          style={{ width: `${percent}%` }}
        />
      </div>

      <ul className="mt-2 space-y-1">
        {requirements.map((req) => (
          <li
            key={req.id}
            className={`flex items-center gap-1.5 text-xs ${req.met ? "text-success-500" : "text-muted-dark"}`}
          >
            <span aria-hidden="true">{req.met ? "✓" : "○"}</span>
            {req.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
