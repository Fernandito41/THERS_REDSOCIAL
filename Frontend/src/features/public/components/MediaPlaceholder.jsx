import { IoImageOutline, IoPlayOutline } from "react-icons/io5";

// Reserva el espacio visual para foto/video real de THERS. Mientras `src`
// venga vacío (informationContent.js) se ve el placeholder de abajo; en
// cuanto se le pase un `src` real, renderiza la imagen/video de verdad --
// no hace falta tocar EditorialCard ni este componente de nuevo.
export default function MediaPlaceholder({ type = "image", src, poster, alt = "", className = "" }) {
  const Icon = type === "video" ? IoPlayOutline : IoImageOutline;

  if (type === "image" && src) {
    return <img src={src} alt={alt} className={`rounded-[24px] object-cover ${className}`} />;
  }

  if (type === "video" && src) {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    return (
      <video
        className={`rounded-[24px] object-cover ${className}`}
        src={src}
        poster={poster}
        autoPlay={!reduceMotion}
        muted
        loop
        playsInline
        aria-label={alt}
      />
    );
  }

  return (
    <div
      className={`relative flex items-center justify-center rounded-[24px] border border-dashed border-line dark:border-line-dark bg-gradient-to-br from-pulse-50 to-canvas dark:from-pulse-900/20 dark:to-canvas-dark overflow-hidden ${className}`}
    >
      <div className="flex flex-col items-center gap-2 text-muted dark:text-muted-dark">
        <span className="flex items-center justify-center w-12 h-12 rounded-full bg-surface dark:bg-surface-dark shadow-soft text-pulse-600 dark:text-pulse-300">
          <Icon size={20} aria-hidden="true" />
        </span>
        <span className="text-xs font-medium text-center px-4">
          {type === "video" ? "Video" : "Imagen"} — próximamente
        </span>
      </div>
    </div>
  );
}
