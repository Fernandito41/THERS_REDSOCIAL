import { useState } from "react";
import {
  IoHeart,
  IoHeartOutline,
  IoChatbubbleOutline,
  IoArrowRedoOutline,
  IoBookmark,
  IoBookmarkOutline,
  IoEllipsisHorizontal,
  IoLocationOutline,
  IoPlayCircle,
  IoMusicalNotes,
} from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import MoodBadge from "./MoodBadge";

function CapsuleBody({ capsule }) {
  if ((capsule.type === "photo" || capsule.type === "video") && capsule.image) {
    return (
      <div className="group relative mt-3 h-96 w-full rounded-[24px] overflow-hidden bg-canvas dark:bg-canvas-dark">
        <img
          src={capsule.image}
          alt={capsule.alt || ""}
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"
        />
        {capsule.type === "video" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/15">
            <IoPlayCircle size={56} className="text-white/90 drop-shadow-lg" />
          </div>
        )}
      </div>
    );
  }

  if (capsule.type === "music") {
    return (
      <div className="mt-3 rounded-[24px] bg-gradient-to-tr from-ink to-[#2A2A38] p-5 flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center shrink-0 animate-mood-glow">
          <IoMusicalNotes size={26} className="text-pulse-400" />
        </div>
        <div className="min-w-0">
          <p className="text-white font-semibold truncate">{capsule.track.title}</p>
          <p className="text-white/60 text-sm truncate">{capsule.track.artist}</p>
        </div>
      </div>
    );
  }

  if (capsule.type === "thought" && capsule.text) {
    return (
      <div className="mt-3 rounded-[24px] bg-pulse-50 dark:bg-pulse-900/20 px-6 py-8">
        <p className="text-ink dark:text-ink-dark text-xl font-semibold leading-snug tracking-tight text-center">
          “{capsule.text}”
        </p>
      </div>
    );
  }

  return null;
}

export default function CapsuleCard({ capsule, currentUser }) {
  const [liked, setLiked] = useState(false);
  const [pop, setPop] = useState(false);
  const [likes, setLikes] = useState(capsule.likes);
  const [saved, setSaved] = useState(false);
  const [savePop, setSavePop] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(capsule.comments);
  const [commentInput, setCommentInput] = useState("");
  const [copied, setCopied] = useState(false);

  const toggleLike = () => {
    setLiked((prev) => !prev);
    setLikes((prev) => (liked ? prev - 1 : prev + 1));
    setPop(true);
    setTimeout(() => setPop(false), 350);
  };

  const toggleSave = () => {
    setSaved((prev) => !prev);
    setSavePop(true);
    setTimeout(() => setSavePop(false), 350);
  };

  const handleAddComment = (e) => {
    e.preventDefault();
    if (!commentInput.trim()) return;

    setComments((prev) => [
      ...prev,
      { id: prev.length + 1, author: currentUser.name, text: commentInput.trim() },
    ]);
    setCommentInput("");
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(`https://thers.app/capsula/${capsule.id}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Portapapeles no disponible -- sin acción adicional.
    }
  };

  return (
    <article className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft hover:shadow-lift transition-shadow overflow-hidden animate-capsule-in">
      <div className="flex items-start justify-between px-5 pt-5">
        <div className="flex items-center gap-3">
          <Avatar name={capsule.user.name} photo={capsule.user.photo} size="w-11 h-11" />
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-ink dark:text-ink-dark font-semibold text-sm leading-tight">
                {capsule.user.name}
              </p>
              {capsule.mood && <MoodBadge mood={capsule.mood} />}
            </div>
            <p className="text-muted dark:text-muted-dark text-xs flex items-center gap-1 mt-0.5">
              @{capsule.user.username} · {capsule.timestamp}
              {capsule.location && (
                <span className="flex items-center gap-0.5">
                  <IoLocationOutline size={12} /> {capsule.location}
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label="Más opciones de la cápsula"
            className="text-muted hover:text-ink dark:hover:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark p-2 rounded-full transition"
          >
            <IoEllipsisHorizontal size={18} />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-10 z-10 w-40 bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-2xl shadow-lift py-1 animate-float-in">
              <button
                onClick={() => setMenuOpen(false)}
                className="w-full text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
              >
                Copiar enlace
              </button>
              <button
                onClick={() => setMenuOpen(false)}
                className="w-full text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
              >
                Ocultar
              </button>
              <button
                onClick={() => setMenuOpen(false)}
                className="w-full text-left px-4 py-2 text-sm text-ember-600 hover:bg-canvas dark:hover:bg-canvas-dark"
              >
                Reportar
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="px-5 pt-2">
        {capsule.type !== "thought" && capsule.text && (
          <p className="text-ink/90 dark:text-ink-dark/90 text-[15px] leading-relaxed">{capsule.text}</p>
        )}

        {capsule.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {capsule.hashtags.map((tag) => (
              <span
                key={tag}
                className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-pulse-50 dark:bg-pulse-900/30 text-pulse-700 dark:text-pulse-300"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="px-5">
        <CapsuleBody capsule={capsule} />
      </div>

      <div className="px-5 pt-3 flex items-center justify-between text-xs text-muted dark:text-muted-dark">
        <span>{likes} likes</span>
        <button
          onClick={() => setShowComments((prev) => !prev)}
          className="hover:text-ink dark:hover:text-ink-dark transition"
        >
          {comments.length} comentarios
        </button>
      </div>

      <div className="px-2 pb-2 pt-2 mt-1 border-t border-line dark:border-line-dark flex items-center justify-around">
        <button
          onClick={toggleLike}
          aria-pressed={liked}
          className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm transition hover:bg-canvas dark:hover:bg-canvas-dark ${
            liked ? "text-ember-500" : "text-muted dark:text-muted-dark"
          }`}
        >
          {liked ? (
            <IoHeart size={20} className={pop ? "animate-pop-like" : ""} />
          ) : (
            <IoHeartOutline size={20} />
          )}
          Like
        </button>

        <button
          onClick={() => setShowComments((prev) => !prev)}
          className="flex items-center gap-2 px-3 py-2 rounded-full text-sm text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
        >
          <IoChatbubbleOutline size={20} />
          Comentar
        </button>

        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-3 py-2 rounded-full text-sm text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
        >
          <IoArrowRedoOutline size={20} />
          {copied ? "¡Copiado!" : "Compartir"}
        </button>

        <button
          onClick={toggleSave}
          aria-pressed={saved}
          className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm transition hover:bg-canvas dark:hover:bg-canvas-dark ${
            saved ? "text-pulse-600" : "text-muted dark:text-muted-dark"
          }`}
        >
          {saved ? (
            <IoBookmark size={20} className={savePop ? "animate-pop-like" : ""} />
          ) : (
            <IoBookmarkOutline size={20} />
          )}
          Guardar
        </button>
      </div>

      {showComments && (
        <div className="px-5 pb-5 border-t border-line dark:border-line-dark pt-3 space-y-3">
          {comments.map((comment) => (
            <div key={comment.id} className="flex items-start gap-2">
              <Avatar name={comment.author} size="w-7 h-7 text-xs" />
              <div className="bg-canvas dark:bg-canvas-dark rounded-2xl px-3 py-2 text-sm">
                <span className="text-ink dark:text-ink-dark font-medium mr-1">{comment.author}</span>
                <span className="text-muted dark:text-muted-dark">{comment.text}</span>
              </div>
            </div>
          ))}

          <form onSubmit={handleAddComment} className="flex items-center gap-2 pt-1">
            <Avatar name={currentUser.name} size="w-7 h-7 text-xs" />
            <input
              type="text"
              value={commentInput}
              onChange={(e) => setCommentInput(e.target.value)}
              placeholder="Escribe un comentario..."
              aria-label="Escribir un comentario"
              className="flex-1 bg-canvas dark:bg-canvas-dark border border-transparent rounded-full px-4 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
            />
          </form>
        </div>
      )}
    </article>
  );
}
