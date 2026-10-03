/**
 * "hace 5 min", "ayer", "12 oct". Pensado para listas: corto y sin dependencias.
 * `now` se inyecta para poder probar la función con una fecha fija.
 */
export function formatRelativeTime(iso: string, now: Date = new Date()): string {
  const then = new Date(iso);
  const time = then.getTime();
  if (Number.isNaN(time)) return '';

  const seconds = Math.max(0, Math.floor((now.getTime() - time) / 1000));
  if (seconds < 45) return 'ahora';

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `hace ${Math.max(1, minutes)} min`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `hace ${hours} h`;

  const days = Math.floor(hours / 24);
  if (days === 1) return 'ayer';
  if (days < 7) return `hace ${days} d`;

  const sameYear = then.getFullYear() === now.getFullYear();
  return then.toLocaleDateString('es', {
    day: 'numeric',
    month: 'short',
    ...(sameYear ? {} : { year: 'numeric' }),
  });
}

/** Hora corta de un mensaje: "14:05". */
export function formatClock(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' });
}
