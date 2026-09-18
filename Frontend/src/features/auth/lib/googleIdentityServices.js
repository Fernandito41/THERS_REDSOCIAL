// Carga del script oficial de Google Identity Services
// (ADR-012-google-sign-in.md §Decisión, FASE 2: "utiliza los mecanismos
// oficiales y actuales de Google") -- sin ninguna librería npm de por
// medio (ni `@react-oauth/google` ni similar): Frontend/package.json no
// tenía ninguna dependencia de Google, y este script es lo único que la
// integración necesita (mismo criterio de "no agregar dependencias sin
// justificarlas" que el resto de THERS).
//
// El script se carga una única vez por sesión de navegador, cacheado en
// esta misma promesa a nivel de módulo -- si dos componentes (Login y
// Register nunca están montados a la vez, pero por si acaso) intentan
// inicializar Google Identity Services, ambos esperan la misma carga en
// vez de inyectar el `<script>` dos veces.

const SCRIPT_SRC = "https://accounts.google.com/gsi/client";

let loadPromise = null;

export function loadGoogleIdentityServices() {
  if (typeof window !== "undefined" && window.google?.accounts?.id) {
    return Promise.resolve(window.google);
  }

  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if (window.google?.accounts?.id) {
        resolve(window.google);
      } else {
        reject(new Error("Google Identity Services no se inicializó correctamente."));
      }
    };
    script.onerror = () => {
      loadPromise = null; // permite reintentar en el próximo montaje
      reject(new Error("No se pudo cargar el script de Google Identity Services."));
    };
    document.head.appendChild(script);
  });

  return loadPromise;
}
