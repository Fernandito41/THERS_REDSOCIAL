import Icon from "@shared/components/Icon";
import { coverGradient } from "../data/profileIdentity";

/**
 * Portada del perfil — sección 1 de REF-PROFILE-01.
 *
 * Medidas de la referencia: alto 288px (`h-72`), radio 16px, borde 1px,
 * degradado oscuro sobre la imagen y botón «Cambiar portada» arriba a la
 * derecha.
 *
 * QUÉ CAMBIA RESPECTO DE LA MAQUETA, y por qué:
 *
 *  · La referencia usa una FOTOGRAFÍA de portada. No existe subida de
 *    archivos ni columna de portada ratificada (DATABASE_ARCHITECTURE.md
 *    §4.B), así que se conserva el sistema de degradados que la persona ya
 *    elige en este repositorio (`data/profileIdentity.js`). Inventar una foto
 *    sería fabricar contenido del usuario; el archivo maestro §5.7 prohíbe
 *    además descargar imágenes nuevas para sustituir las referencias.
 *
 *  · La referencia muestra abajo a la derecha un indicador «Audio Espacial
 *    48kHz · Lossless» con un punto verde pulsante. NO se reproduce: el
 *    archivo maestro §8.7 exige que «Lossless», «48kHz» y «audio espacial»
 *    describan capacidades reales comprobadas, y §10.2 prohíbe presentar un
 *    estado «en vivo» fijo del cliente.
 */
export default function ProfileCover({ cover, onChangeCover }) {
  return (
    <div className="relative h-44 w-full overflow-hidden rounded-th-card border border-th-border bg-th-surface-raised shadow-th-card sm:h-56 lg:h-72">
      <div
        className="h-full w-full bg-cover bg-center"
        style={{ backgroundImage: coverGradient(cover) }}
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
