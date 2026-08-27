import { useLanguage } from "@shared/i18n";

// Selector de idioma reutilizado en el menú de perfil (AppShell), Configuración
// y las pantallas de autenticación. Con solo 2 idiomas (Fase 1: es/en), un
// control segmentado es más claro que un <select> -- si se agrega un tercer
// idioma, revisar si sigue siendo la mejor forma o conviene un dropdown.
export default function LanguageSwitcher({ className = "" }) {
  const { language, setLanguage, languages, t } = useLanguage();

  return (
    <div
      role="group"
      aria-label={t("language.label")}
      className={`inline-flex items-center gap-0.5 rounded-full border border-line dark:border-line-dark p-0.5 ${className}`}
    >
      {languages.map((lang) => (
        <button
          key={lang.code}
          type="button"
          onClick={() => setLanguage(lang.code)}
          aria-pressed={language === lang.code}
          className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide transition ${
            language === lang.code
              ? "bg-pulse-600 text-white"
              : "text-muted dark:text-muted-dark hover:text-ink dark:hover:text-ink-dark"
          }`}
        >
          {lang.code}
        </button>
      ))}
    </div>
  );
}
