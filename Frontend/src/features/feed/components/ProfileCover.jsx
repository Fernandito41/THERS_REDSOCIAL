import Icon from "@shared/components/Icon";
import { coverGradient } from "../data/profileIdentity";

/**
 * Portada del perfil — sección 1 de REF-PROFILE-01.
 *
 * Medidas de la referencia: alto 288px (`h-72`), radio 16px, borde 1px,
 * degradado oscuro sobre la imagen y botón «Cambiar portada» arriba a la
 * derecha.
 *
 * `coverUrl` es la foto subida por la persona (`cover_url`, ADR-015); sin
 * ella se usa el degradé elegido (`cover`), nunca una foto inventada.
 *
 * NO se reproduce de la maqueta el indicador «Audio Espacial 48kHz ·
 * Lossless»: el archivo maestro §8.7/§10.2 exige que describa capacidades
 * reales comprobadas.
 */
export default function ProfileCover({ cover, coverUrl, onChangeCover }) {
  return (
    <div className="relative h-44 w-full overflow-hidden rounded-th-card border border-th-border bg-th-surface-raised shadow-th-card sm:h-56 lg:h-72">
      <div
        className="h-full w-full bg-cover bg-center"
        style={{
          backgroundImage: coverUrl ? `url("${coverUrl}")` : coverGradient(cover),
        }}
        aria-hidden="true"
      />
      <div
        className="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-transparent to-slate-900/20"
        aria-hidden="true"
      />

      <button
        type="button"
        onClick={onChangeCover}
        className="absolute right-4 top-4 inline-flex min-h-[44px] items-center gap-2 rounded-th-input bg-white/90 px-3.5 py-2 text-label-md font-bold text-slate-800 shadow-th-card backdrop-blur-md transition-colors th-focus-ring hover:bg-white"
      >
        <Icon name="photo_camera" size={18} />
        Cambiar portada
      </button>
    </div>
  );
}
