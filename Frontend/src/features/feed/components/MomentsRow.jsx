import { useState } from "react";
import Icon from "@shared/components/Icon";
import Avatar from "@shared/components/Avatar";
import MomentViewer from "./MomentViewer";
import { MOODS, mockMoments } from "../data/mockData";

/**
 * Momentos — sección 1 de REF-FEED-01.
 *
 * Composición de la referencia: cabecera «Momentos Activos» con
 * `auto_awesome_motion` y enlace «Ver todos», seguida de un carrusel
 * horizontal con snap. La primera tarjeta es la de creación propia (borde
 * discontinuo, avatar con insignia «+»), después las de otras personas.
 *
 * Medidas literales del prototipo: tarjetas de 128×184px, radio 16px.
 *
 * DATOS: fixture (`data/mockData`). No existe endpoint de momentos; se rotula
 * como ejemplo en vez de presentarse como actividad real de la red
 * (archivo maestro §9.5).
 */
export default function MomentsRow({ currentUser }) {
  const [activeIndex, setActiveIndex] = useState(null);

  return (
    <section aria-label="Momentos" className="flex flex-col gap-2">
      <header className="flex items-center justify-between gap-2 px-1">
        <h2 className="flex items-center gap-2 text-label-lg font-bold text-th-fg-strong">
          <Icon name="auto_awesome_motion" size={18} className="text-th-brand" />
          Momentos Activos
          <span className="text-label-md font-normal italic text-th-fg-subtle">(ejemplo)</span>
        </h2>
        <span className="flex items-center gap-0.5 text-label-md font-semibold text-th-fg-muted">
          Ver todos
          <Icon name="chevron_right" size={16} />
        </span>
      </header>

      <div className="th-scrollbar-none flex snap-x snap-mandatory items-center gap-4 overflow-x-auto pb-1">
        {/* Tarjeta de creación propia */}
        <div className="group relative flex h-[184px] w-[128px] shrink-0 snap-start cursor-pointer flex-col justify-between overflow-hidden rounded-th-card border-2 border-dashed border-th-border bg-th-surface p-2 shadow-th-card transition-all hover:border-th-border-strong hover:shadow-th-hover">
          <div className="relative w-fit">
            <Avatar name={currentUser?.name} size="w-10 h-10 text-sm" />
            <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-th-pill bg-th-brand shadow-th-card">
              <Icon name="add" size={14} className="text-th-on-brand" />
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-label-md font-bold text-th-fg-strong">Tu momento</span>
            <span className="text-label-md text-th-fg-muted">Compartir ahora</span>
          </div>
        </div>

        {mockMoments.map((moment, index) => (
          <button
            key={moment.id}
            type="button"
            onClick={() => setActiveIndex(index)}
            aria-label={`Ver el momento de ${moment.name}, mood ${MOODS[moment.mood]?.label || ""}`}
            className="group relative h-[184px] w-[128px] shrink-0 snap-start overflow-hidden rounded-th-card shadow-th-card ring-2 ring-transparent transition-all th-focus-ring hover:ring-th-brand"
          >
            <img
              src={moment.image}
              alt=""
              loading="lazy"
              className="absolute inset-0 h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/75 via-slate-900/10 to-slate-900/10" />

            <span className="absolute left-2 top-2">
              <Avatar name={moment.name} photo={moment.photo} size="w-9 h-9 text-xs" ring />
            </span>

            <span
              className="absolute right-2 top-2 h-2.5 w-2.5 rounded-th-pill ring-2 ring-white/80"
              aria-hidden="true"
              style={{ backgroundColor: MOODS[moment.mood]?.color }}
            />

            <span className="absolute inset-x-2 bottom-2 flex flex-col text-left">
              <span className="truncate text-label-lg font-bold text-white drop-shadow">
                {moment.name}
              </span>
              <span className="text-label-md text-white/75">{moment.time}</span>
            </span>
          </button>
        ))}
      </div>

      {activeIndex !== null && (
        <MomentViewer
          moments={mockMoments}
          index={activeIndex}
          onClose={() => setActiveIndex(null)}
          onPrev={() => setActiveIndex((i) => Math.max(0, i - 1))}
          onNext={() => setActiveIndex((i) => Math.min(mockMoments.length - 1, i + 1))}
        />
      )}
    </section>
  );
}
