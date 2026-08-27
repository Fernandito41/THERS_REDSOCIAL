// Fase 1 de i18n: español (idioma nativo de THERS) + inglés. Agregar un
// idioma nuevo es: 1) crear locales/<code>.json con las mismas claves que
// es.json, 2) sumar la entrada acá. No requiere tocar ningún componente.
export const SUPPORTED_LANGUAGES = [
  { code: "es", labelKey: "language.es" },
  { code: "en", labelKey: "language.en" },
];

export const DEFAULT_LANGUAGE = "es";

export const SUPPORTED_LANGUAGE_CODES = SUPPORTED_LANGUAGES.map((lang) => lang.code);
