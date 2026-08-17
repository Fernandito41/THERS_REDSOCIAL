import { useState } from "react";

// Google/Apple no tienen soporte en el backend todavía (sin OAuth provider,
// sin /api/auth/google ni /api/auth/apple -- confirmado revisando backend/).
// Este hook solo maneja el aviso honesto al hacer click; NUNCA simula un
// login exitoso. Cada página decide cómo se ve el aviso.
export function useOAuthNotice() {
  const [notice, setNotice] = useState(null);

  const notify = (provider) => {
    setNotice(provider);
    setTimeout(() => setNotice(null), 5000);
  };

  return { notice, notify };
}
