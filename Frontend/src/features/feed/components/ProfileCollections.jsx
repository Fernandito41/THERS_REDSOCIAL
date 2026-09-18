import Icon from "@shared/components/Icon";

/**
 * Colecciones Destacadas — sección 3 de REF-PROFILE-01.
 *
 * La referencia muestra una cabecera («Colecciones Destacadas», «6 Canales»,
 * «Archivos permanentes del perfil», botón «+ Nueva») y una fila de tarjetas
 * con portada: Rutas Noche, Estudio Synth Setup 2026, En Vivo, Cafés Top.
 *
 * NO HAY BACKEND DE COLECCIONES. No existe entidad ni endpoint: el modelo de
 * datos implementado solo cubre `users`, `posts`, `likes`, `comments`,
 * `follows` y `notifications` (DATABASE_ARCHITECTURE.md §4.B).
 *
 * Por eso se conserva la SECCIÓN —el archivo maestro §8.3 pide preservar las
 * colecciones destacadas y §1 prohíbe omitir bloques por ser laboriosos— pero
 * con su estado vacío honesto en vez de cuatro tarjetas inventadas. El botón
 * «+ Nueva» queda deshabilitado con explicación accesible (§7.1), no
 * simulando una creación que no persistiría.
 */
export default function ProfileCollections() {
  return (
    <section
      aria-labelledby="profile-collections-title"
      className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-5 shadow-th-card"
    >
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-0.5">
          <h2
            id="profile-collections-title"
            className="text-label-lg font-bold text-th-fg-strong"
          >
            Colecciones Destacadas
          </h2>
          <p className="text-body-sm text-th-fg-muted">Archivos permanentes del perfil</p>
        </div>

        <button
          type="button"
          disabled
          aria-describedby="profile-collections-hint"
          className="inline-flex min-h-[44px] items-center gap-1.5 rounded-th-input border border-th-border px-3.5 py-2 text-label-md font-bold text-th-fg-subtle opacity-60"
        >
          <Icon name="add" size={18} />
          Nueva
          <span id="profile-collections-hint" className="sr-only">
            Crear colección: todavía no disponible, falta soporte en el servidor
          </span>
        </button>
      </header>

      <div className="flex flex-col items-start gap-2 rounded-th-input border border-dashed border-th-border bg-th-surface-subtle p-6">
        <p className="text-body-md text-th-fg-muted">
          Todavía no hay colecciones: THERS aún no tiene dónde guardarlas.
        </p>
        <p className="text-body-sm text-th-fg-subtle">
          Cuando exista el modelo de colecciones, tus canales destacados aparecerán aquí.
        </p>
      </div>
    </section>
  );
}
