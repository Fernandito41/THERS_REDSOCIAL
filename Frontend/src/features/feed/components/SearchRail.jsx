import Icon from "@shared/components/Icon";
import { mockSuggestions, mockTopics } from "../data/mockData";

/**
 * Rail derecho de Buscar — REF-SEARCH-01, columna `lg:col-span-4`.
 *
 * Conserva los cuatro bloques de la referencia y su orden: Creadores
 * Recomendados, Temas Sugeridos, Listas de la Comunidad y la caja de estado
 * inferior.
 *
 * PROCEDENCIA:
 *  · Creadores y Temas: FIXTURE, rotulado en pantalla. No hay endpoint que
 *    liste usuarios ni tendencias (archivo maestro §9.5: fixture y dato real
 *    no se mezclan en silencio).
 *  · Listas de la Comunidad: no existe el modelo de listas/colecciones
 *    (DATABASE_ARCHITECTURE.md §4.B) -> estado vacío honesto.
 *  · Caja de estado: la referencia afirma «streaming sin compresión de audio
 *    PCM y renderizado nativo 4K a 60 FPS». NO se reproduce ese texto: es una
 *    declaración de capacidad que el producto no tiene (§8.7/§10.2). Se
 *    sustituye por el estado real del buscador.
 */
export default function SearchRail({ followingIds, onToggleFollow }) {
  return (
    <aside className="flex flex-col gap-6 lg:col-span-4">
      <RailCard title="Creadores Recomendados" note="Ejemplo: sin endpoint de creadores todavía">
        <ul className="flex flex-col gap-3">
          {mockSuggestions.slice(0, 3).map((person) => {
            const isFollowing = followingIds.has(person.id);
            return (
              <li key={person.id} className="flex items-center justify-between gap-2">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-th-pill bg-th-surface-raised text-label-md font-bold text-th-fg-muted">
                    {initialsOf(person)}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-body-sm font-semibold text-th-fg-strong">
                      {person.name}
                    </p>
                    <p className="truncate text-label-md text-th-fg-muted">@{person.username}</p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onToggleFollow(person.id)}
                  aria-pressed={isFollowing}
                  className={`shrink-0 rounded-th-pill border px-3 py-1.5 text-label-md font-bold transition-colors th-focus-ring ${
                    isFollowing
                      ? "border-th-border bg-th-surface text-th-fg-muted hover:bg-th-surface-raised"
                      : "border-th-brand bg-th-brand text-th-on-brand hover:bg-th-brand-hover"
                  }`}
                >
                  {isFollowing ? "Siguiendo" : "Seguir"}
                </button>
              </li>
            );
          })}
        </ul>
      </RailCard>

      <RailCard title="Temas Sugeridos" note="Ejemplo: sin endpoint de tendencias todavía">
        <ul className="flex flex-wrap gap-2">
          {mockTopics.map((topic) => (
            <li key={topic.id}>
              <span className="inline-flex items-center rounded-th-pill border border-th-border bg-th-surface-subtle px-3 py-1 text-label-md font-semibold text-th-fg-muted">
                #{topic.tag}
              </span>
            </li>
          ))}
        </ul>
      </RailCard>

      <RailCard title="Listas de la Comunidad">
        <p className="text-body-sm text-th-fg-muted">
          Todavía no existen las listas: THERS no tiene aún un modelo de colecciones donde
          guardarlas.
        </p>
      </RailCard>

      <div className="flex items-start gap-3 rounded-th-card border border-th-border bg-th-surface-subtle p-4">
        <Icon name="info" size={20} className="mt-0.5 shrink-0 text-th-fg-subtle" />
        <p className="text-body-sm text-th-fg-muted">
          El buscador recorre las publicaciones ya cargadas desde el servidor. Todavía no hay un
          endpoint de búsqueda ni contenido de vídeo indexado.
        </p>
      </div>
    </aside>
  );
}

function RailCard({ title, note, children }) {
  return (
    <section className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-6 shadow-th-card">
      <h2 className="text-label-lg font-bold text-th-fg-strong">{title}</h2>
      {children}
      {note && <p className="text-label-md italic text-th-fg-subtle">{note}</p>}
    </section>
  );
}

function initialsOf(user) {
  const source = user?.name || user?.username || "";
  const parts = source.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
