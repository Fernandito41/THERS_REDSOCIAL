import Icon from "@shared/components/Icon";

/**
 * Rail derecho del perfil — sección 6 de REF-PROFILE-01.
 *
 * La referencia trae cuatro módulos, en este orden: «Actividad del Perfil»,
 * «Mis Cápsulas Top», «Nodos Frecuentes» y «Conexiones Mutuas». Se conservan
 * los cuatro (archivo maestro §8.3 y §1: no omitir bloques), con el estado
 * honesto que corresponde a cada uno.
 *
 *  · Actividad del Perfil — la maqueta muestra «+24% este mes», «148 hrs de
 *    escucha» y «4.8k oyentes en vivo». NO hay telemetría ni reproductor: no
 *    se inventa ninguna métrica (§10.2).
 *  · Mis Cápsulas Top — ES CALCULABLE: son los posts propios ordenados por
 *    `likes_count`, que viaja real con cada post (ADR-005). Único módulo del
 *    rail con datos reales.
 *  · Nodos Frecuentes — requiere lugares/Radar, sin backend (§8.8).
 *  · Conexiones Mutuas — `follows` existe (ADR-007) pero no hay endpoint que
 *    liste seguidores ni calcule mutuos; solo hay contadores agregados.
 */
export default function ProfileRail({ ownCapsules = [] }) {
  const topCapsules = [...ownCapsules]
    .sort((a, b) => (b.likes_count ?? 0) - (a.likes_count ?? 0))
    .filter((capsule) => (capsule.likes_count ?? 0) > 0)
    .slice(0, 3);

  return (
    <aside className="flex w-full flex-col gap-6 xl:w-th-rail xl:shrink-0">
      <RailCard title="Actividad del Perfil" icon="monitoring">
        <Unavailable
          text="Sin datos de actividad: THERS todavía no registra telemetría de escucha ni de alcance."
        />
      </RailCard>

      <RailCard title="Mis Cápsulas Top" icon="trending_up">
        {topCapsules.length > 0 ? (
          <ul className="flex flex-col gap-3">
            {topCapsules.map((capsule) => (
              <li key={capsule.id} className="flex flex-col gap-1">
                <p className="line-clamp-2 text-body-sm font-semibold text-th-fg-strong">
                  {capsule.content}
                </p>
                <span className="inline-flex items-center gap-1.5 text-label-md text-th-fg-muted">
                  <Icon name="favorite" size={14} />
                  {capsule.likes_count} {capsule.likes_count === 1 ? "me gusta" : "me gusta"}
                  <span aria-hidden="true">·</span>
                  <Icon name="chat_bubble" size={14} />
                  {capsule.comments_count}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <Unavailable text="Todavía ninguna de tus cápsulas tiene me gusta." />
        )}
      </RailCard>

      <RailCard title="Nodos Frecuentes" icon="location_on">
        <Unavailable text="Los lugares dependen de Radar, que aún no tiene servicio conectado." />
      </RailCard>

      <RailCard title="Conexiones Mutuas" icon="group">
        <Unavailable text="Sin endpoint que liste seguidores: solo existen los contadores agregados." />
      </RailCard>
    </aside>
  );
}

function RailCard({ title, icon, children }) {
  return (
    <section className="flex flex-col gap-3 rounded-th-card border border-th-border bg-th-surface p-4 shadow-th-card">
      <header className="flex items-center justify-between gap-2">
        <h2 className="text-label-lg font-bold text-th-fg-strong">{title}</h2>
        <Icon name={icon} size={18} className="text-th-fg-subtle" />
      </header>
      {children}
    </section>
  );
}

function Unavailable({ text }) {
  return <p className="text-body-sm text-th-fg-muted">{text}</p>;
}
