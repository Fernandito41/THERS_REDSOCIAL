import { Link } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { mockSuggestions, mockTopics } from "../data/mockData";

/**
 * Rail derecho del Feed — sección 6 de REF-FEED-01 (≈340px).
 *
 * Conserva los cuatro módulos de la referencia y su orden: mini-tarjeta de
 * perfil con métricas, «Personas que resuenan», «Temas en tendencia» y
 * «Cápsulas para ti».
 *
 * PROCEDENCIA DE LOS DATOS — mezclada a propósito, y señalada en pantalla:
 *  · Perfil y métricas: REALES. `followers_count` viene de GET /api/users/me
 *    (ADR-007) y las publicaciones se cuentan sobre los posts ya cargados.
 *  · Personas y temas: FIXTURE (`data/mockData`). No hay endpoint de
 *    sugerencias ni de tendencias; se rotulan como ejemplo en vez de pasar
 *    por datos reales (archivo maestro §9.5: "datos reales y fixtures no
 *    deben mezclarse silenciosamente en una pantalla").
 *
 * La referencia dibuja un indicador «En línea» en la mini-tarjeta. NO se
 * reproduce como estado activo: no existe sistema de presencia y el archivo
 * maestro §10.2 prohíbe presentarlo como capacidad real.
 */
export default function DiscoveryRail({ currentUser, capsules, followingIds, onToggleFollow }) {
  const postCount = capsules.filter((capsule) => capsule.author?.id === currentUser?.id).length;

  return (
    <aside className="flex w-full flex-col gap-6 xl:w-th-rail xl:shrink-0">
      {/* 1. Mini-tarjeta de perfil + métricas — datos reales */}
      <div className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-4 shadow-th-card">
        <div className="flex items-center justify-between gap-3">
          <Link to="/profile" className="flex min-w-0 items-center gap-3 rounded-th-sm th-focus-ring">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-th-pill bg-th-brand text-headline-sm font-bold text-th-on-brand">
              {initialsOf(currentUser)}
            </span>
            <span className="flex min-w-0 flex-col">
              <span className="truncate text-label-lg font-semibold text-th-fg-strong">
                {currentUser?.name}
              </span>
              <span className="truncate text-body-sm text-th-fg-muted">
                @{currentUser?.username}
              </span>
            </span>
          </Link>
        </div>

        <div className="grid grid-cols-2 gap-1 rounded-th-input border border-th-border-subtle bg-th-surface-subtle p-2 text-center">
          <Metric value={postCount} label="Publicaciones" />
          <Metric value={currentUser?.followers_count ?? 0} label="Seguidores" />
        </div>
      </div>

      {/* 2. Personas que resuenan — fixture rotulado */}
      <RailCard
        title="Personas que resuenan"
        icon="sync_alt"
        note="Ejemplo: sin endpoint de sugerencias todavía"
      >
        <ul className="flex flex-col gap-3">
          {mockSuggestions.map((person) => {
            const isFollowing = followingIds.has(person.id);
            return (
              <li key={person.id} className="flex items-center justify-between gap-2">
                <div className="flex min-w-0 items-center gap-2">
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

      {/* 3. Temas en tendencia — fixture rotulado */}
      <RailCard
        title="Temas en tendencia"
        icon="trending_up"
        note="Ejemplo: sin endpoint de tendencias todavía"
      >
        <ul className="flex flex-col gap-2">
          {mockTopics.map((topic) => (
            <li key={topic.id}>
              <Link
                to={`/search?q=${encodeURIComponent("#" + topic.tag)}`}
                className="group flex items-center justify-between gap-2 rounded-th-sm px-1 py-1.5 transition-colors th-focus-ring hover:bg-th-surface-subtle"
              >
                <span className="min-w-0">
                  <span className="block truncate text-body-sm font-semibold text-th-brand-fg">
                    #{topic.tag}
                  </span>
                  <span className="block text-label-md text-th-fg-muted">
                    {topic.capsules} cápsulas
                  </span>
                </span>
                <Icon
                  name="arrow_outward"
                  size={16}
                  className="shrink-0 text-th-fg-subtle transition-colors group-hover:text-th-brand"
                />
              </Link>
            </li>
          ))}
        </ul>
      </RailCard>

      {/* 4. Cápsulas para ti — el módulo existe en la referencia, pero no hay
          fuente de recomendación. Se muestra su estado vacío honesto en vez de
          inventar una recomendación (archivo maestro §9.4). */}
      <RailCard title="Cápsulas para ti" icon="auto_stories">
        <div className="flex flex-col items-start gap-2 rounded-th-input border border-dashed border-th-border bg-th-surface-subtle p-4">
          <p className="text-body-sm text-th-fg-muted">
            Todavía no hay recomendaciones: falta el servicio que las calcula.
          </p>
          <Link
            to="/search"
            className="text-label-lg font-bold text-th-brand-fg th-focus-ring hover:underline"
          >
            Explorar cápsulas
          </Link>
        </div>
      </RailCard>
    </aside>
  );
}

function RailCard({ title, icon, note, children }) {
  return (
    <section className="flex flex-col gap-3 rounded-th-card border border-th-border bg-th-surface p-4 shadow-th-card">
      <header className="flex items-center justify-between gap-2">
        <h2 className="text-label-lg font-bold text-th-fg-strong">{title}</h2>
        <Icon name={icon} size={18} className="text-th-fg-subtle" />
      </header>
      {children}
      {note && <p className="text-label-md italic text-th-fg-subtle">{note}</p>}
    </section>
  );
}

function Metric({ value, label }) {
  return (
    <div className="flex flex-col">
      <span className="text-label-lg font-bold text-th-fg-strong">{value}</span>
      <span className="text-label-md text-th-fg-muted">{label}</span>
    </div>
  );
}

function initialsOf(user) {
  const source = user?.name || user?.username || "";
  const parts = source.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
