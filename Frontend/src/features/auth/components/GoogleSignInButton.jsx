import { useEffect, useRef, useState } from "react";
import { useLanguage } from "@shared/i18n";
import { loadGoogleIdentityServices } from "../lib/googleIdentityServices";

// Botón real de "Continuar con Google" (ADR-012-google-sign-in.md, FASE 16).
// `google.accounts.id.renderButton()` dibuja el botón oficial de Google
// dentro de un iframe que Google controla -- nunca se dibuja un logo propio
// ni se copia el diseño: es literalmente el componente de Google,
// respetando sus lineamientos de marca por construcción.
//
// Deliberadamente "tonto": solo carga el script, inicializa, y llama a
// `onCredential(idToken)` cuando Google entrega una credencial exitosa --
// no sabe nada sobre THERS, `POST /api/auth/google`, ni maneja su propio
// estado de carga hacia el backend (eso lo hacen Login.jsx/Register.jsx,
// mismo patrón que ya usan para el formulario tradicional con isSubmitting).
//
// Nota sobre "popup cerrado"/"autenticación cancelada" (FASE 16): Google
// Identity Services no expone un callback de cancelación para el flujo de
// botón estándar (a diferencia de One Tap, que sí tiene razones de
// descarte) -- si la persona cierra la ventana de selección de cuenta,
// simplemente no pasa nada y el botón queda disponible para reintentar. No
// se simula un estado de "cancelado" que la librería no reporta de verdad.
export default function GoogleSignInButton({ onCredential, onError, disabled = false }) {
  const containerRef = useRef(null);
  const { language } = useLanguage();
  const [failedToLoad, setFailedToLoad] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    if (!clientId) {
      console.warn(
        "[GoogleSignInButton] VITE_GOOGLE_CLIENT_ID no está definida -- el " +
          "botón de Google no puede inicializarse. Definir esa variable en " +
          "Frontend/.env (ver .env.example)."
      );
      setFailedToLoad(true);
      return;
    }

    loadGoogleIdentityServices()
      .then((google) => {
        if (cancelled || !containerRef.current) return;

        google.accounts.id.initialize({
          client_id: clientId,
          // El Frontend nunca interpreta el credential -- lo reenvía tal
          // cual a POST /api/auth/google, que lo verifica de verdad.
          callback: (response) => onCredential(response.credential),
        });

        const width = Math.min(
          Math.max(containerRef.current.getBoundingClientRect().width || 320, 200),
          400
        );

        google.accounts.id.renderButton(containerRef.current, {
          type: "standard",
          theme: "outline",
          size: "large",
          shape: "pill",
          text: "continue_with",
          logo_alignment: "left",
          locale: language,
          width,
        });
      })
      .catch((err) => {
        console.error("[GoogleSignInButton]", err);
        if (!cancelled) {
          setFailedToLoad(true);
          onError?.(err);
        }
      });

    return () => {
      cancelled = true;
    };
    // Solo re-inicializa si cambia el idioma -- `onCredential`/`onError` son
    // callbacks estables desde quien los pasa (Login.jsx/Register.jsx), no
    // hace falta re-montar el botón de Google por su identidad de función
    // (el plugin eslint-plugin-react-hooks no está instalado en este
    // proyecto, ver Frontend/package.json -- sin regla que exija listarlos).
  }, [language]);

  if (failedToLoad) {
    // Sin botón falso ni mensaje de error intrusivo -- el resto del
    // formulario (email/password) sigue funcionando igual; el problema (env
    // var faltante) ya se advirtió por consola para quien desarrolla.
    return null;
  }

  return (
    <div
      ref={containerRef}
      className={`w-full flex justify-center ${disabled ? "opacity-50 pointer-events-none" : ""}`}
    />
  );
}
