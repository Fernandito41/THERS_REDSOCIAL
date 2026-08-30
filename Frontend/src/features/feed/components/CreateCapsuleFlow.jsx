import { useState } from "react";
import { IoClose } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import Spinner from "@shared/components/Spinner";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";

// POST /api/posts (ADR-004-posts-minimal-model.md) solo acepta `content` --
// mood/imagen/hashtags/ubicación que este composer ofrecía antes no tienen
// dónde persistirse todavía, así que se quitan del formulario en vez de
// dejar que la persona los llene y se pierdan en silencio (peor que no
// mostrarlos). Vuelven cuando cada uno tenga su propio ADR/columna.
const MAX_CONTENT_LENGTH = 2000;

export default function CreateCapsuleFlow({ currentUser, onClose, onSubmit }) {
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();
  const { t } = useLanguage();

  const trimmedLength = content.trim().length;
  const canPublish = trimmedLength > 0 && trimmedLength <= MAX_CONTENT_LENGTH && !isSubmitting;

  const handlePublish = async () => {
    if (!canPublish) return;

    setIsSubmitting(true);
    try {
      await onSubmit(content.trim());
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink/60 backdrop-blur-sm flex items-center justify-center px-4" onClick={onClose}>
      <div
        className="w-full max-w-lg bg-surface/95 dark:bg-surface-dark/95 backdrop-blur-xl border border-line dark:border-line-dark rounded-[28px] shadow-lift animate-float-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-5 py-4 border-b border-line dark:border-line-dark">
          <h3 className="text-ink dark:text-ink-dark font-bold text-lg flex-1">Crear Cápsula</h3>
          <button
            onClick={onClose}
            aria-label="Cerrar"
            disabled={isSubmitting}
            className="text-muted hover:bg-canvas dark:hover:bg-canvas-dark p-2 rounded-full transition focus:outline-none focus-visible:ring-2 focus-visible:ring-pulse-500 disabled:opacity-50"
          >
            <IoClose size={20} />
          </button>
        </div>

        <div className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <Avatar name={currentUser.name} size="w-10 h-10" />
            <div>
              <p className="text-ink dark:text-ink-dark font-medium text-sm">{currentUser.name}</p>
              <p className="text-muted text-xs">@{currentUser.username}</p>
            </div>
          </div>

          <textarea
            autoFocus
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="¿Qué quieres expresar?"
            rows={5}
            disabled={isSubmitting}
            aria-label="Contenido de la cápsula"
            className="w-full bg-transparent text-ink dark:text-ink-dark placeholder-muted resize-none focus:outline-none text-lg disabled:opacity-60"
          />

          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-muted dark:text-muted-dark">
              Fotos, video, música, mood y ubicación llegan pronto.
            </p>
            <span
              className={`text-xs shrink-0 ml-3 ${
                trimmedLength > MAX_CONTENT_LENGTH ? "text-ember-500 font-semibold" : "text-muted"
              }`}
            >
              {trimmedLength}/{MAX_CONTENT_LENGTH}
            </span>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-line dark:border-line-dark flex gap-3">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="flex-1 py-3 rounded-full font-semibold border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition disabled:opacity-50"
          >
            Cancelar
          </button>

          <button
            onClick={handlePublish}
            disabled={!canPublish}
            className={`flex-1 py-3 rounded-full font-semibold transition flex items-center justify-center gap-2 ${
              canPublish
                ? "bg-pulse-600 hover:bg-pulse-700 text-white shadow-glow"
                : "bg-line dark:bg-line-dark text-muted cursor-not-allowed"
            }`}
          >
            {isSubmitting && <Spinner />}
            {isSubmitting ? "Publicando..." : "Publicar Cápsula"}
          </button>
        </div>
      </div>
    </div>
  );
}
