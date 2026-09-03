import Avatar from "@shared/components/Avatar";
import { formatRelativeTime } from "../lib/formatRelativeTime";

// Tratamiento dedicado para posts reales de solo texto (GET/POST /api/posts,
// ADR-004-posts-minimal-model.md) -- sin imagen/mood/hashtags/ubicación
// (no existen en el contrato) y sin likes/comentarios (no implementados
// todavía, DATABASE_ARCHITECTURE.md §4.B): mostrar un contador en 0 sería un
// dato falso, así que esa sección directamente no existe acá, en vez de
// fingirla. Tipografía más grande que ocupa el espacio que dejaría una
// imagen, sobre superficie plana: la identidad monocroma del perfil
// (Frontend/src/assets/ideas_perfil.jpeg) deja las tarjetas sin el degradé
// morado que tenían antes, usando solo tokens de tailwind.config.js
// (surface/canvas/line, sombra soft/lift).
export default function CapsuleCard({ capsule }) {
  return (
    <article className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft hover:shadow-lift transition-shadow overflow-hidden animate-capsule-in motion-reduce:animate-none">
      <div className="flex items-center gap-3 px-6 pt-6">
        <Avatar name={capsule.author.name} size="w-11 h-11" />
        <div className="min-w-0">
          <p className="text-ink dark:text-ink-dark font-semibold text-sm leading-tight truncate">
            {capsule.author.name}
          </p>
          <p className="text-muted dark:text-muted-dark text-xs mt-0.5">
            @{capsule.author.username} · {formatRelativeTime(capsule.created_at)}
          </p>
        </div>
      </div>

      <div className="px-6 pt-4 pb-7">
        <p className="text-ink dark:text-ink-dark text-lg sm:text-xl font-medium leading-snug whitespace-pre-wrap break-words">
          {capsule.content}
        </p>
      </div>
    </article>
  );
}
