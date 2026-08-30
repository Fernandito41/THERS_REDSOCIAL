// Núcleo de traducción propio, sin dependencia nueva (mismo criterio que el
// resto del Frontend: Context API para AuthContext/ToastContext, hook propio
// para useTheme). Claves con notación de puntos ("auth.login.title"),
// interpolación simple "{{var}}" para valores dinámicos (contador de no
// leídas, nombre de proveedor OAuth, edad mínima).

function getByPath(source, path) {
  return path
    .split(".")
    .reduce((acc, part) => (acc && typeof acc === "object" ? acc[part] : undefined), source);
}

function interpolate(template, vars) {
  if (!vars) return template;
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => (key in vars ? String(vars[key]) : match));
}

// `t(key, vars)`: string traducida, con fallback al locale por defecto y,
// en último caso, a la propia clave (visible en desarrollo si falta una
// traducción, en vez de romper el render).
// `tList(key)`: variante para arrays (nombres de mes, días de la semana) --
// no aplica interpolación, no tiene sentido en una lista.
export function createTranslator(locale, fallbackLocale) {
  function t(key, vars) {
    const value = getByPath(locale, key);
    if (typeof value === "string") return interpolate(value, vars);

    const fallback = getByPath(fallbackLocale, key);
    if (typeof fallback === "string") return interpolate(fallback, vars);

    return key;
  }

  function tList(key) {
    const value = getByPath(locale, key);
    if (Array.isArray(value)) return value;

    const fallback = getByPath(fallbackLocale, key);
    return Array.isArray(fallback) ? fallback : [];
  }

  return { t, tList };
}
