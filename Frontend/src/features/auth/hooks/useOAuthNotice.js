import { useState } from "react";

// Apple no tiene soporte en el backend todavía (sin OAuth provider, sin
// /api/auth/apple -- confirmado revisando backend/). Este hook solo maneja
// el aviso honesto al hacer click; NUNCA simula un login exitoso. Cada
// página decide cómo se ve el aviso.
//
// Google SÍ tiene soporte real desde ADR-012-google-sign-in.md
// (POST /api/auth/google) -- Login.jsx/Register.jsx ya no llaman a
// `notify("google")`, usan GoogleSignInButton.jsx en su lugar. Este hook
// sigue existiendo solo para Apple.
export function useOAuthNotice() {
  const [notice, setNotice] = useState(null);

  const notify = (provider) => {
    setNotice(provider);
    setTimeout(() => setNotice(null), 5000);
  };

  return { notice, notify };
}
