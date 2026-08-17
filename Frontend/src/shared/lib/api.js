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
export function getErrorMessage(error) {
  if (!error.response) {
    return "No se pudo conectar con el servidor. Intentá de nuevo más tarde.";
  }

  const { status, data } = error.response;

  if (status === 401) {
    return "Email o contraseña incorrectos.";
  }

  if (status === 409) {
    return "Ya existe una cuenta con ese email.";
  }

  if (status === 400) {
    return (data && data.msg) || "Revisá los datos ingresados.";
  }

  return "Ocurrió un error inesperado. Intentá de nuevo más tarde.";
}