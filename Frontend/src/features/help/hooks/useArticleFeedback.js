import { useState } from "react";

const STORAGE_PREFIX = "thers_help_feedback_";

// Feedback "¿Te resultó útil?" persistido por artículo en este dispositivo --
// no hay endpoint de Help Center en el backend todavía (API_CONTRACT.md solo
// documenta /login y /register), así que no se simula un envío a un servidor
// que no existe. Queda aislado por slug para no mezclar votos entre artículos.
function readVote(slug) {
  try {
    return localStorage.getItem(STORAGE_PREFIX + slug) || null;
  } catch {
    return null;
  }
}

export function useArticleFeedback(slug) {
  const [vote, setVote] = useState(() => readVote(slug));

  const submitVote = (value) => {
    try {
      localStorage.setItem(STORAGE_PREFIX + slug, value);
    } catch {
      // Almacenamiento no disponible (modo privado, cuotas) -- el voto sigue
      // funcionando en memoria para esta sesión.
    }
    setVote(value);
  };

  return { vote, submitVote };
}
