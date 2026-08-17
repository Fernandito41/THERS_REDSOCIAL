import { useRef, useState } from "react";
import {
  IoClose,
  IoImageOutline,
  IoVideocamOutline,
  IoChatbubbleOutline,
  IoMusicalNotesOutline,
  IoHappyOutline,
  IoLocationOutline,
  IoArrowBack,
} from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { MOODS } from "../data/mockData";

const IMAGE_OPTIONS = [
  "from-pulse-500 to-pulse-300",
  "from-pulse-700 to-pulse-400",
  "from-pulse-800 to-pulse-500",
];

// Tonos elegidos para verse bien sobre fondo claro Y oscuro -- se evitan los
// extremos (100-300 se lavan sobre blanco, 700-800 casi desaparecen sobre el
// fondo oscuro de la tarjeta).
const TYPES = [
  { id: "photo", label: "Foto", icon: IoImageOutline, color: "text-pulse-500 dark:text-pulse-400" },
  { id: "video", label: "Video", icon: IoVideocamOutline, color: "text-pulse-400 dark:text-pulse-300" },
  { id: "thought", label: "Pensamiento", icon: IoChatbubbleOutline, color: "text-pulse-600 dark:text-pulse-400" },
  { id: "music", label: "Música", icon: IoMusicalNotesOutline, color: "text-pulse-500 dark:text-pulse-400" },
  { id: "mood", label: "Mood", icon: IoHappyOutline, color: "text-pulse-400 dark:text-pulse-300" },
  { id: "location", label: "Ubicación", icon: IoLocationOutline, color: "text-pulse-600 dark:text-pulse-400" },
];

export default function CreateCapsuleFlow({ currentUser, onClose, onSubmit }) {
  const [type, setType] = useState(null);
  const [text, setText] = useState("");
  const [mood, setMood] = useState(null);
  const [hashtagsInput, setHashtagsInput] = useState("");
  const [location, setLocation] = useState("");
  const [imageIndex, setImageIndex] = useState(null);
  const [trackTitle, setTrackTitle] = useState("");
  const [trackArtist, setTrackArtist] = useState("");
  const locationRef = useRef(null);

  const selectType = (id) => {
    if (id === "location") {
      setType((prev) => prev || "thought");
      setTimeout(() => locationRef.current?.focus(), 50);
      return;
    }
    setType(id);
  };

  const canPublish =
    type === "music"
      ? trackTitle.trim().length > 0
      : text.trim().length > 0 ||
        Boolean(mood) ||
        location.trim().length > 0 ||
        ((type === "photo" || type === "video") && imageIndex !== null);

  const handlePublish = () => {
    if (!canPublish) return;

    const hashtags = hashtagsInput
      .split(/[\s,]+/)
      .map((tag) => tag.replace(/^#/, "").trim())
      .filter(Boolean);

    onSubmit({
      type,
      text: text.trim(),
      mood,
      hashtags,
      location: location.trim() || null,
      media: (type === "photo" || type === "video") && imageIndex !== null ? IMAGE_OPTIONS[imageIndex] : null,
      track: type === "music" ? { title: trackTitle.trim(), artist: trackArtist.trim() || "Desconocido" } : null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-ink/60 backdrop-blur-sm flex items-center justify-center px-4" onClick={onClose}>
      <div
        className="w-full max-w-lg bg-surface/95 dark:bg-surface-dark/95 backdrop-blur-xl border border-line dark:border-line-dark rounded-[28px] shadow-lift animate-float-in max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-5 py-4 border-b border-line dark:border-line-dark sticky top-0 bg-surface/95 dark:bg-surface-dark/95 backdrop-blur-xl z-10">
          {type && (
            <button
              onClick={() => setType(null)}
              aria-label="Volver a elegir tipo de cápsula"
              className="text-muted hover:bg-canvas dark:hover:bg-canvas-dark p-2 rounded-full transition"
            >
              <IoArrowBack size={18} />
            </button>
          )}
          <h3 className="text-ink dark:text-ink-dark font-bold text-lg flex-1">
            {type ? "Crear Cápsula" : "¿Qué quieres expresar?"}
          </h3>
          <button
            onClick={onClose}
            aria-label="Cerrar"
            className="text-muted hover:bg-canvas dark:hover:bg-canvas-dark p-2 rounded-full transition"
          >
            <IoClose size={20} />
          </button>
        </div>

        {!type && (
          <div className="p-5 grid grid-cols-3 gap-3">
            {TYPES.map(({ id, label, icon: Icon, color }) => (
              <button
                key={id}
                onClick={() => selectType(id)}
                className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-line dark:border-line-dark hover:border-pulse-300 hover:bg-pulse-50 dark:hover:bg-pulse-900/20 transition"
              >
                <Icon size={26} className={color} />
                <span className="text-xs font-medium text-ink dark:text-ink-dark">{label}</span>
              </button>
            ))}
          </div>
        )}

        {type && (
          <div className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <Avatar name={currentUser.name} size="w-10 h-10" />
              <div>
                <p className="text-ink dark:text-ink-dark font-medium text-sm">{currentUser.name}</p>
                <p className="text-muted text-xs">@{currentUser.username}</p>
              </div>
            </div>

            {type === "music" && (
              <div className="space-y-2 mb-3">
                <input
                  type="text"
                  value={trackTitle}
                  onChange={(e) => setTrackTitle(e.target.value)}
                  placeholder="Título de la canción"
                  className="w-full bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
                />
                <input
                  type="text"
                  value={trackArtist}
                  onChange={(e) => setTrackArtist(e.target.value)}
                  placeholder="Artista"
                  className="w-full bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
                />
              </div>
            )}

            <textarea
              autoFocus={type !== "music"}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={type === "thought" ? "Comparte lo que estás pensando..." : "Agrega una descripción (opcional)"}
              rows={type === "thought" ? 5 : 3}
              className="w-full bg-transparent text-ink dark:text-ink-dark placeholder-muted resize-none focus:outline-none text-base"
            />

            <div className="flex flex-wrap gap-2 mt-3">
              {Object.entries(MOODS).map(([id, { label, color }]) => (
                <button
                  key={id}
                  onClick={() => setMood(mood === id ? null : id)}
                  className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border transition ${
                    mood === id
                      ? "bg-pulse-600 border-pulse-600 text-white"
                      : "border-line dark:border-line-dark text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                  }`}
                >
                  <span
                    aria-hidden="true"
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: mood === id ? "#fff" : color }}
                  />
                  {label}
                </button>
              ))}
            </div>

            <input
              type="text"
              value={hashtagsInput}
              onChange={(e) => setHashtagsInput(e.target.value)}
              placeholder="Temas (ej: thers diseño musica)"
              className="w-full mt-3 bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
            />

            <div className="relative mt-2">
              <IoLocationOutline className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input
                ref={locationRef}
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Agregar ubicación (opcional)"
                className="w-full bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg pl-9 pr-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
              />
            </div>

            {(type === "photo" || type === "video") && (
              <div className="flex items-center gap-2 mt-3">
                <span className="text-xs text-muted">Elige un fondo</span>
                {IMAGE_OPTIONS.map((gradient, index) => (
                  <button
                    key={gradient}
                    onClick={() => setImageIndex(imageIndex === index ? null : index)}
                    aria-label={`Fondo ${index + 1}`}
                    className={`w-8 h-8 rounded-lg bg-gradient-to-tr ${gradient} ${
                      imageIndex === index ? "ring-2 ring-pulse-500" : "opacity-70 hover:opacity-100"
                    } transition`}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {type && (
          <div className="px-5 py-4 border-t border-line dark:border-line-dark flex gap-3 sticky bottom-0 bg-surface/95 dark:bg-surface-dark/95 backdrop-blur-xl">
            <button
              onClick={onClose}
              className="flex-1 py-3 rounded-full font-semibold border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
            >
              Cancelar
            </button>

            <button
              onClick={handlePublish}
              disabled={!canPublish}
              className={`flex-1 py-3 rounded-full font-semibold transition ${
                canPublish
                  ? "bg-pulse-600 hover:bg-pulse-700 text-white shadow-glow"
                  : "bg-line dark:bg-line-dark text-muted cursor-not-allowed"
              }`}
            >
              Publicar Cápsula
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
