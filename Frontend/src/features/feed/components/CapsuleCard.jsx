import { useState } from "react";
import { IoChatbubbleOutline, IoHeart, IoHeartOutline, IoSend } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import Spinner from "@shared/components/Spinner";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { getErrorMessage } from "@shared/lib/api";
import { formatRelativeTime } from "../lib/formatRelativeTime";

// Tratamiento dedicado para posts reales de solo texto (GET/POST /api/posts,
// ADR-004-posts-minimal-model.md) -- sin imagen/mood/hashtags/ubicación (no
// existen en el contrato). Likes, comentarios y seguir al autor sí son
// reales:
// - El botón de like (`likes_count`/`liked_by_me`, GET/POST/DELETE
//   /api/posts, ADR-005-likes-minimal-model.md) usa el mismo ícono
//   (IoHeart/IoHeartOutline) y color (ember-500) que el resto de la UI ya
//   usa para "me gusta" (ProfileTabs.jsx, Notifications.jsx).
// - El panel de comentarios (`comments_count`, GET/POST
//   /api/posts/<id>/comments, ADR-006-comments-minimal-model.md) se carga
//   bajo demanda -- no tiene sentido traer el hilo completo de cada post
//   del feed de antemano, solo el del que el usuario realmente abre.
// - El control "Seguir"/"Siguiendo" (`author.is_followed_by_me`, GET/POST/
//   DELETE /api/users/<id>/follow, ADR-007-follows-minimal-model.md) solo
//   se muestra sobre autores de posts reales -- es la única fuente de
//   usuarios reales visibles hoy en la UI, el panel de sugerencias de
//   Home.jsx sigue siendo mock (ADR-007 §No objetivos).
// Tipografía más grande que ocupa el espacio que dejaría una imagen, sobre
// superficie plana: la identidad monocroma del perfil
// (Frontend/src/assets/ideas_perfil.jpeg) deja las tarjetas sin el degradé
// morado que tenían antes, usando solo tokens de tailwind.config.js
// (surface/canvas/line, sombra soft/lift).
export default function CapsuleCard({
  capsule,
  currentUserId,
  onToggleLike,
  onLoadComments,
  onPostComment,
  onToggleFollowAuthor,
}) {
  const toast = useToast();
  const { t } = useLanguage();

  const [isOpen, setOpen] = useState(false);
  const [comments, setComments] = useState(null);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState("");
  const [posting, setPosting] = useState(false);

  const handleToggleComments = async () => {
    const willOpen = !isOpen;
    setOpen(willOpen);

    if (willOpen && comments === null) {
      setLoading(true);
      try {
        const loaded = await onLoadComments(capsule.id);
        setComments(loaded);
      } catch (error) {
        toast.error(getErrorMessage(error, t));
        setOpen(false);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || posting) return;

    setPosting(true);
    try {
      const comment = await onPostComment(capsule.id, content);
      setComments((prev) => [...(prev ?? []), comment]);
      setDraft("");
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setPosting(false);
    }
  };

  return (
    <article className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft hover:shadow-lift transition-shadow overflow-hidden animate-capsule-in motion-reduce:animate-none">
      <div className="flex items-center gap-3 px-6 pt-6">
        <Avatar name={capsule.author.name} size="w-11 h-11" />
        <div className="min-w-0 flex-1">
          <p className="text-ink dark:text-ink-dark font-semibold text-sm leading-tight truncate">
            {capsule.author.name}
          </p>
          <p className="text-muted dark:text-muted-dark text-xs mt-0.5">
            @{capsule.author.username} · {formatRelativeTime(capsule.created_at)}
          </p>
        </div>

        {capsule.author.id !== currentUserId && (
          <button
            type="button"
            onClick={() => onToggleFollowAuthor?.(capsule.author.id)}
            aria-pressed={capsule.author.is_followed_by_me}
            className={`shrink-0 px-3 py-1 rounded-full text-xs font-semibold border transition ${
              capsule.author.is_followed_by_me
                ? "bg-canvas dark:bg-canvas-dark border-line dark:border-line-dark text-muted hover:bg-line dark:hover:bg-line-dark"
                : "bg-pulse-600 border-pulse-600 text-white hover:bg-pulse-700"
            }`}
          >
            {capsule.author.is_followed_by_me ? "Siguiendo" : "Seguir"}
          </button>
        )}
      </div>

      <div className="px-6 pt-4 pb-3">
        <p className="text-ink dark:text-ink-dark text-lg sm:text-xl font-medium leading-snug whitespace-pre-wrap break-words">
          {capsule.content}
        </p>
      </div>

      <div className="px-6 pb-6">
        <div className="flex items-center gap-1 -ml-3">
          <button
            type="button"
            onClick={() => onToggleLike?.(capsule.id)}
            aria-pressed={capsule.liked_by_me}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition ${
              capsule.liked_by_me
                ? "text-ember-500"
                : "text-muted dark:text-muted-dark hover:text-ember-500"
            }`}
          >
            {capsule.liked_by_me ? <IoHeart size={19} /> : <IoHeartOutline size={19} />}
            {capsule.likes_count > 0 && <span>{capsule.likes_count}</span>}
          </button>

          <button
            type="button"
            onClick={handleToggleComments}
            aria-expanded={isOpen}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium text-muted dark:text-muted-dark hover:text-pulse-600 dark:hover:text-pulse-300 transition"
          >
            <IoChatbubbleOutline size={19} />
            {capsule.comments_count > 0 && <span>{capsule.comments_count}</span>}
          </button>
        </div>

        {isOpen && (
          <div className="mt-3 pt-4 border-t border-line dark:border-line-dark space-y-4">
            {loading ? (
              <div className="flex items-center gap-2 text-muted dark:text-muted-dark py-2">
                <Spinner size={16} />
                <span className="text-sm">Cargando comentarios...</span>
              </div>
            ) : comments && comments.length === 0 ? (
              <p className="text-sm text-muted dark:text-muted-dark">
                Todavía no hay comentarios. Sé el primero en comentar.
              </p>
            ) : (
              <ul className="space-y-3">
                {comments?.map((comment) => (
                  <li key={comment.id} className="flex items-start gap-2.5">
                    <Avatar name={comment.author.name} size="w-7 h-7" />
                    <div className="min-w-0 flex-1 bg-canvas dark:bg-canvas-dark rounded-2xl px-3.5 py-2">
                      <p className="text-xs font-semibold text-ink dark:text-ink-dark">
                        {comment.author.name}{" "}
                        <span className="font-normal text-muted dark:text-muted-dark">
                          · {formatRelativeTime(comment.created_at)}
                        </span>
                      </p>
                      <p className="text-sm text-ink dark:text-ink-dark whitespace-pre-wrap break-words">
                        {comment.content}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}

            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <input
                type="text"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Escribí un comentario..."
                disabled={posting}
                maxLength={1000}
                className="flex-1 bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark rounded-full px-4 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500 disabled:opacity-60"
              />
              <button
                type="submit"
                disabled={!draft.trim() || posting}
                aria-label="Publicar comentario"
                className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center bg-pulse-600 hover:bg-pulse-700 disabled:opacity-40 disabled:hover:bg-pulse-600 text-white transition"
              >
                {posting ? <Spinner size={16} /> : <IoSend size={15} />}
              </button>
            </form>
          </div>
        )}
      </div>
    </article>
  );
}
