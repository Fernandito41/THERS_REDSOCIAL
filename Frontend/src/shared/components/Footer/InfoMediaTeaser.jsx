import { Link } from "react-router-dom";
import { IoImagesOutline, IoPlayCircleOutline } from "react-icons/io5";
import { INFO_MEDIA_ITEMS } from "./infoMedia";

// Reserva el espacio para el primer contenido multimedia de "Información"
// (infoMedia.js). Mientras esa lista esté vacía, muestra un placeholder
// explícito -- nunca contenido inventado haciéndose pasar por oficial.
export default function InfoMediaTeaser() {
  const item = INFO_MEDIA_ITEMS[0];

  if (!item) {
    return (
      <div className="mt-1 flex items-center gap-2.5 rounded-xl border border-dashed border-line dark:border-line-dark px-2.5 py-2.5 text-muted dark:text-muted-dark">
        <IoImagesOutline size={16} className="shrink-0" aria-hidden="true" />
        <span className="text-xs">Contenido multimedia — próximamente</span>
      </div>
    );
  }

  const isVideo = item.type === "video";

  return (
    <Link
      to={item.link}
      className="group flex items-center gap-2.5 rounded-xl px-2 py-1.5 -mx-2 hover:bg-canvas dark:hover:bg-canvas-dark transition-colors"
    >
      <span className="relative shrink-0 w-12 h-9 rounded-lg overflow-hidden bg-line dark:bg-line-dark">
        <img
          src={isVideo ? item.thumbnail : item.src}
          alt=""
          className="w-full h-full object-cover"
        />
        {isVideo && (
          <IoPlayCircleOutline
            size={18}
            className="absolute inset-0 m-auto text-white drop-shadow"
            aria-hidden="true"
          />
        )}
      </span>
      <span className="min-w-0">
        <span className="block text-sm text-ink dark:text-ink-dark leading-tight truncate">{item.title}</span>
        <span className="block text-xs text-muted dark:text-muted-dark mt-0.5 truncate">{item.description}</span>
      </span>
    </Link>
  );
}
