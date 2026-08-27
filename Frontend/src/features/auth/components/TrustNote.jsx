import { IoShieldCheckmarkOutline } from "react-icons/io5";
import { useLanguage } from "@shared/i18n";

// Microcopy de confianza mostrado antes del botón de "Crear cuenta" -- texto
// exacto aprobado en la tarea, sin afirmaciones técnicas que Backend todavía
// no pueda garantizar (sin mención de cifrado, 2FA, etc.).
export default function TrustNote() {
  const { t } = useLanguage();

  return (
    <div className="flex items-start gap-3 bg-black/30 border border-line-dark rounded-xl px-4 py-3">
      <IoShieldCheckmarkOutline className="text-pulse-400 shrink-0 mt-0.5" size={18} aria-hidden="true" />
      <div>
        <p className="text-sm font-semibold text-ink-dark">{t("auth.trustNote.title")}</p>
        <p className="text-xs text-muted-dark mt-0.5">{t("auth.trustNote.body")}</p>
      </div>
    </div>
  );
}
