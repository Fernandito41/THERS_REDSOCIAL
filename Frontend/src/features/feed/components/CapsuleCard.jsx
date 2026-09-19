import { useState } from "react";
import { Link } from "react-router-dom";
import Icon from "@shared/components/Icon";
import Avatar from "@shared/components/Avatar";
import Spinner from "@shared/components/Spinner";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { getErrorMessage } from "@shared/lib/api";
import { formatRelativeTime } from "../lib/formatRelativeTime";

// Tarjeta de publicación del stream — sección 4 de REF-FEED-01.
//
// Composición de la referencia: cabecera (avatar, nombre, distintivo,
// control de seguir, handle · tiempo, menú), cuerpo de texto, chip de
// ubicación y barra social con favorite / chat_bubble / bookmark_add / share.
// Superficie blanca, borde 1px, radio 16px, padding 24px.
//
// QUÉ ES REAL Y QUÉ NO (archivo maestro §8.1 y §9.4):
//  · Like (favorite): REAL — POST/DELETE /api/posts/<id>/like, ADR-005.
//    Actualización optimista con rollback, gestionada por AppShell.
//  · Comentarios (chat_bubble): REAL — GET/POST /api/posts/<id>/comments,
//    ADR-006. El hilo se pide bajo demanda al abrir el panel, no de antemano.
//  · Seguir al autor: REAL — POST/DELETE /api/users/<id>/follow, ADR-007.
//  · Guardar (bookmark_add) y compartir (share): SIN ENDPOINT. Se dibujan
//    como en la referencia pero deshabilitados y con explicación accesible;
//    no se simula que funcionen.
//  · Distintivo «verified»: NO se reproduce. El contrato no expone
//    verificación y el archivo maestro §8.4 prohíbe otorgarla por fixture.
//  · Chip de ubicación: NO se reproduce. `post` no tiene campo de lugar
//    (ADR-004); inventarlo sería fabricar un dato.
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
    <article className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-6 shadow-th-card transition-colors hover:border-th-border-strong">
      <header className="flex items-start gap-3">
        <Avatar name={capsule.author.name} size="w-10 h-10" />

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="truncate text-label-lg font-bold text-th-fg-strong">
              {capsule.author.name}
            </p>

            {capsule.author.id !== currentUserId && (
              <button
                type="button"
                onClick={() => onToggleFollowAuthor?.(capsule.author.id)}
                aria-pressed={capsule.author.is_followed_by_me}
                className={`shrink-0 rounded-th-pill border px-2.5 py-0.5 text-label-md font-bold transition-colors th-focus-ring ${
                  capsule.author.is_followed_by_me
                    ? "border-th-border bg-th-surface-subtle text-th-fg-muted hover:bg-th-surface-raised"
                    : "border-th-brand bg-th-brand text-th-on-brand hover:bg-th-brand-hover"
                }`}
              >
                {capsule.author.is_followed_by_me ? "Siguiendo" : "Seguir"}
              </button>
            )}

            {capsule.author.id !== currentUserId && (
              // GET /api/conversations (ADR-013) solo lista gente con la que
              // ya hay al menos un mensaje -- este es el punto de entrada
              // real para empezar una conversación nueva. Messages.jsx lee
              // estos mismos parámetros para abrir un hilo vacío listo para
              // escribir, sin inventar un endpoint de búsqueda de usuarios
              // (no existe todavía, DATABASE_ARCHITECTURE.md §4.B).
              <Link
                to={`/messages?to=${capsule.author.id}&name=${encodeURIComponent(capsule.author.name)}&username=${encodeURIComponent(capsule.author.username)}`}
                aria-label={`Mandarle un mensaje a ${capsule.author.name}`}
                className="shrink-0 rounded-th-pill border border-th-border bg-th-surface p-1.5 text-th-fg-muted transition-colors th-focus-ring hover:bg-th-surface-subtle"
              >
                <Icon name="mail" size={16} />
              </Link>
            )}
          </div>

          <p className="mt-0.5 truncate text-body-sm text-th-fg-muted">
            @{capsule.author.username} · {formatRelativeTime(capsule.created_at)}
          </p>
        </div>
      </header>

      <p className="whitespace-pre-wrap break-words text-body-lg text-th-fg">{capsule.content}</p>

      <div className="flex flex-wrap items-center gap-1 border-t border-th-border-subtle pt-3">
        <button
          type="button"
          onClick={() => onToggleLike?.(capsule.id)}
          aria-pressed={capsule.liked_by_me}
          aria-label={capsule.liked_by_me ? "Quitar me gusta" : "Me gusta"}
          className={`inline-flex min-h-[44px] items-center gap-1.5 rounded-th-pill px-3 py-1.5 text-label-lg transition-colors th-focus-ring ${
            capsule.liked_by_me
              ? "text-th-danger-accent"
              : "text-th-fg-muted hover:bg-th-surface-subtle hover:text-th-danger-accent"
          }`}
        >
          <Icon name="favorite" size={20} fill={capsule.liked_by_me ? 1 : 0} />
          {capsule.likes_count > 0 && <span>{capsule.likes_count}</span>}
        </button>

        <button
          type="button"
          onClick={handleToggleComments}
          aria-expanded={isOpen}
          aria-label="Comentarios"
          className="inline-flex min-h-[44px] items-center gap-1.5 rounded-th-pill px-3 py-1.5 text-label-lg text-th-fg-muted transition-colors th-focus-ring hover:bg-th-surface-subtle hover:text-th-brand"
        >
          <Icon name="chat_bubble" size={20} />
          {capsule.comments_count > 0 && <span>{capsule.comments_count}</span>}
        </button>

        {/* Presentes en la referencia, sin endpoint que los respalde. */}
        <PendingAction id={`save-${capsule.id}`} icon="bookmark_add" label="Guardar" />
        <PendingAction id={`share-${capsule.id}`} icon="share" label="Compartir" />
      </div>

      {isOpen && (
        <div className="flex flex-col gap-4 border-t border-th-border-subtle pt-4">
          {loading ? (
            <div className="flex items-center gap-2 py-2 text-th-fg-muted" role="status">
              <Spinner size={16} />
              <span className="text-body-sm">Cargando comentarios...</span>
            </div>
          ) : comments && comments.length === 0 ? (
            <p className="text-body-sm text-th-fg-muted">
              Todavía no hay comentarios. Sé el primero en comentar.
            </p>
          ) : (
            <ul className="flex flex-col gap-3">
              {comments?.map((comment) => (
                <li key={comment.id} className="flex items-start gap-2.5">
                  <Avatar name={comment.author.name} size="w-7 h-7" />
                  <div className="min-w-0 flex-1 rounded-th-card bg-th-surface-subtle px-3.5 py-2">
                    <p className="text-label-md font-bold text-th-fg-strong">
                      {comment.author.name}{" "}
                      <span className="font-normal text-th-fg-muted">
                        · {formatRelativeTime(comment.created_at)}
                      </span>
                    </p>
                    <p className="whitespace-pre-wrap break-words text-body-sm text-th-fg">
                      {comment.content}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <label htmlFor={`comment-${capsule.id}`} className="sr-only">
              Escribir un comentario
            </label>
            <input
              id={`comment-${capsule.id}`}
              type="text"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Escribí un comentario..."
              disabled={posting}
              maxLength={1000}
              className="min-h-[44px] flex-1 rounded-th-pill border border-th-border bg-th-surface-subtle px-4 py-2 text-body-sm text-th-fg placeholder:text-th-fg-muted transition-colors th-focus-ring disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={!draft.trim() || posting}
              aria-label="Publicar comentario"
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-th-pill bg-th-brand text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-40 disabled:hover:bg-th-brand"
            >
              {posting ? <Spinner size={16} /> : <Icon name="send" size={18} />}
            </button>
          </form>
        </div>
      )}
    </article>
  );
}

/** Acción dibujada en la referencia que todavía no tiene soporte de servidor. */
function PendingAction({ id, icon, label }) {
  return (
    <button
      type="button"
      disabled
      aria-describedby={`${id}-hint`}
      className="inline-flex min-h-[44px] items-center gap-1.5 rounded-th-pill px-3 py-1.5 text-label-lg text-th-fg-subtle opacity-60"
    >
      <Icon name={icon} size={20} />
      <span className="sr-only">{label}</span>
      <span id={`${id}-hint`} className="sr-only">
        {label}: todavía no disponible, falta soporte en el servidor
      </span>
    </button>
  );
}
