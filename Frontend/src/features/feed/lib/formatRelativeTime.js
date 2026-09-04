// Formatea `created_at` (ISO 8601, tal como lo devuelve GET/POST /api/posts,
// ADR-004-posts-minimal-model.md) a texto relativo en español, mismo estilo
// que ya usaban los timestamps de mockCapsules ("Hace 2 h").
export function formatRelativeTime(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";

  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return "Ahora";
  if (diffMin < 60) return `Hace ${diffMin} min`;

  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `Hace ${diffHours} h`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `Hace ${diffDays} d`;

  return date.toLocaleDateString("es", { day: "numeric", month: "short" });
}
