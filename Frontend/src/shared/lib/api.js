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