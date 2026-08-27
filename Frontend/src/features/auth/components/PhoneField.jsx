import { useId } from "react";
import { IoCallOutline } from "react-icons/io5";
import { useLanguage } from "@shared/i18n";

// Lista corta y pragmática (no exhaustiva de todos los países del mundo):
// El Salvador primero y por defecto (HB-001 confirma que THERS es un
// proyecto salvadoreño), seguido de la región y algunos códigos frecuentes.
// Ampliar esta lista no requiere tocar ningún otro archivo.
//
// Nombres de país sin traducir a propósito (Fase 1 de i18n, shared/i18n):
// el alcance de esa fase fue navegación/auth/configuración, no este listado.
// Si se traduce, mover country a claves shared/i18n (p. ej. "countries.SV")
// en vez de interpolar el código de idioma acá.
export const COUNTRY_CODES = [
  { code: "+503", country: "El Salvador", flag: "🇸🇻" },
  { code: "+502", country: "Guatemala", flag: "🇬🇹" },
  { code: "+504", country: "Honduras", flag: "🇭🇳" },
  { code: "+505", country: "Nicaragua", flag: "🇳🇮" },
  { code: "+506", country: "Costa Rica", flag: "🇨🇷" },
  { code: "+507", country: "Panamá", flag: "🇵🇦" },
  { code: "+52", country: "México", flag: "🇲🇽" },
  { code: "+57", country: "Colombia", flag: "🇨🇴" },
  { code: "+51", country: "Perú", flag: "🇵🇪" },
  { code: "+54", country: "Argentina", flag: "🇦🇷" },
  { code: "+56", country: "Chile", flag: "🇨🇱" },
  { code: "+34", country: "España", flag: "🇪🇸" },
  { code: "+1", country: "Estados Unidos / Canadá", flag: "🇺🇸" },
];

export const DEFAULT_COUNTRY_CODE = COUNTRY_CODES[0].code;

// Mismo lenguaje visual que TextField/PasswordField (borde, radio, focus ring,
// mensaje de error) pero con un segmento de código de país pegado al input,
// como pidió el wireframe ("+503  0000-0000" en una sola fila).
export default function PhoneField({
  label,
  countryCode,
  onCountryCodeChange,
  error,
  className = "",
  id: idProp,
  ...inputProps
}) {
  const generatedId = useId();
  const id = idProp || generatedId;
  const errorId = `${id}-error`;
  const countrySelectId = `${id}-country`;
  const { t } = useLanguage();
  const resolvedLabel = label || t("auth.phoneField.label");

  return (
    <div className={className}>
      <label htmlFor={id} className="sr-only">
        {resolvedLabel}
      </label>
      <div
        className={`flex items-stretch bg-transparent border rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-pulse-500 ${
          error ? "border-ember-500" : "border-line-dark"
        }`}
      >
        <div className="flex items-center gap-1 pl-3 pr-1.5 border-r border-line-dark shrink-0">
          <IoCallOutline className="text-muted-dark" size={16} aria-hidden="true" />
          <label htmlFor={countrySelectId} className="sr-only">
            {t("auth.phoneField.countryCodeLabel")}
          </label>
          <select
            id={countrySelectId}
            value={countryCode}
            onChange={(e) => onCountryCodeChange(e.target.value)}
            className="bg-transparent text-sm text-ink-dark py-3 pr-1 focus:outline-none"
          >
            {COUNTRY_CODES.map((c) => (
              <option key={c.code + c.country} value={c.code} className="text-ink bg-white">
                {c.flag} {c.code}
              </option>
            ))}
          </select>
        </div>

        <input
          id={id}
          type="tel"
          inputMode="tel"
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className="flex-1 min-w-0 bg-transparent px-3 py-3 text-ink-dark placeholder-muted-dark focus:outline-none"
          {...inputProps}
        />
      </div>
      {error && (
        <p id={errorId} role="alert" className="mt-1.5 text-xs text-ember-400">
          {error}
        </p>
      )}
    </div>
  );
}
