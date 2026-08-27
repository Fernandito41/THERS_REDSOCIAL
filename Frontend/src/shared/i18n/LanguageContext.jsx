import { createContext, useContext, useEffect, useMemo, useState } from "react";
import es from "./locales/es.json";
import en from "./locales/en.json";
import { SUPPORTED_LANGUAGES, SUPPORTED_LANGUAGE_CODES, DEFAULT_LANGUAGE } from "./languages";
import { createTranslator } from "./translate";

const LOCALES = { es, en };
const STORAGE_KEY = "thers_language";

// THERS es un proyecto salvadoreño (HB-001) y nació en español -- español es
// el idioma por defecto la primera vez que alguien entra, igual que
// useTheme.js define el oscuro como tema por defecto. A partir de ahí se
// respeta lo que la persona haya elegido (localStorage), igual que el tema.
function detectInitialLanguage() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored && SUPPORTED_LANGUAGE_CODES.includes(stored)) return stored;

  const browserLanguage = (navigator.language || "").slice(0, 2);
  return SUPPORTED_LANGUAGE_CODES.includes(browserLanguage) ? browserLanguage : DEFAULT_LANGUAGE;
}

const LanguageContext = createContext(undefined);

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(detectInitialLanguage);

  useEffect(() => {
    document.documentElement.lang = language;
    localStorage.setItem(STORAGE_KEY, language);
  }, [language]);

  const setLanguage = (code) => {
    if (!SUPPORTED_LANGUAGE_CODES.includes(code)) return;
    setLanguageState(code);
  };

  const { t, tList } = useMemo(
    () => createTranslator(LOCALES[language], LOCALES[DEFAULT_LANGUAGE]),
    [language]
  );

  const value = { language, setLanguage, languages: SUPPORTED_LANGUAGES, t, tList };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage debe usarse dentro de un LanguageProvider");
  }
  return context;
}
