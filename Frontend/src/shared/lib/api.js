import axios from "axios";

const DEV_FALLBACK_API_URL = "http://127.0.0.1:5000/api";

if (!import.meta.env.VITE_API_URL) {
  console.warn(
    "[api] VITE_API_URL no está definida; usando el valor de desarrollo local " +
    DEV_FALLBACK_API_URL + ". Definir VITE_API_URL en Frontend/.env para otros entornos."
  );
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || DEV_FALLBACK_API_URL
});

// Traduce errores de axios a un mensaje entendible para el usuario, siguiendo
// el contrato de error documentado en API_CONTRACT.md (400/401/409,
// body {"msg": "..."}). Nunca expone detalles internos (stack traces, texto
// crudo del error de red).
//
// `t` es la función de shared/i18n (useLanguage().t) -- se recibe como
// parámetro en vez de importar el contexto acá para que este módulo siga
// siendo un cliente HTTP puro, sin depender de React. El texto que devuelve
// el propio backend (`data.msg`) no se traduce: es contenido que no
// controlamos desde el Frontend.
export function getErrorMessage(error, t) {
  if (!error.response) {
    return t("errors.network");
  }

  const { status, data } = error.response;

  if (status === 401) {
    return t("errors.invalidCredentials");
  }

  if (status === 409) {
    return (data && data.msg) || t("errors.emailInUse");
  }

  if (status === 400) {
    return (data && data.msg) || t("errors.checkData");
  }

  return t("errors.unexpected");
}