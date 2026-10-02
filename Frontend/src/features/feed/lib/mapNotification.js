// Traduce la forma cruda que devuelve GET /api/notifications
// (ADR-008-notifications-minimal-model.md) a la forma que Notifications.jsx
// ya sabe renderizar (heredada de mockNotifications) -- así ese componente
// no necesita reescribirse, solo dejar de recibir datos inventados.
//
// `photo`: nunca se completa -- no existe `avatar_url` ratificada todavía
// (DATABASE_ARCHITECTURE.md §4.B › Perfil, PENDIENTE DE DECISIÓN), mismo
// motivo por el que ningún post/comentario real la tiene. Avatar.jsx ya
// renderiza iniciales sin esta prop.
import { formatRelativeTime } from "./formatRelativeTime";

const DETAIL_BY_TYPE = {
  like: "reaccionó a tu Cápsula",
  comment: "comentó tu Cápsula",
  follow: "comenzó a seguirte",
  // ADR-018-private-accounts.md
  follow_request: "quiere seguirte",
  follow_accepted: "aceptó tu solicitud",
  // ADR-019-mentions.md
  mention: "te mencionó",
};

// "Importante" en el sentido que Notifications.jsx ya usaba para
// mockNotifications (una sección separada, más destacada) -- los eventos de
// relación y las menciones directas ameritan esa jerarquía; like/comment van a
// "Actividad reciente". `follow_request` entra porque pide una acción (hay que
// aprobarla o rechazarla, en Configuración › Privacidad), no solo informa.
// Puramente una regla de presentación del Frontend, no una columna del backend
// (ADR-008 §Modelo de datos no incluye ningún campo de prioridad).
const IMPORTANT_TYPES = new Set([
  "follow",
  "follow_request",
  "follow_accepted",
  "mention",
]);

export function mapNotification(raw) {
  return {
    id: raw.id,
    type: raw.type,
    actor: raw.actor.name,
    detail: DETAIL_BY_TYPE[raw.type] || "",
    time: formatRelativeTime(raw.created_at),
    important: IMPORTANT_TYPES.has(raw.type),
    read: raw.read,
  };
}
