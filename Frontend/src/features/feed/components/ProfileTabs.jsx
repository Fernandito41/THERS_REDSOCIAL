import { useRef } from "react";

// Barra de secciones del perfil — sección 4 de REF-PROFILE-01.
//
// La referencia define TRES pestañas: Publicaciones, Destacadas y Me gusta,
// cada una con su contador, subrayado violeta en la activa y el contador de
// la activa en violeta suave. Se adopta ese conjunto: sustituye a las cinco
// anteriores (Publicaciones/Respuestas/Media/Guardados/Me gusta), que no
// venían de ninguna referencia recibida.
//
// CONTADORES: solo se dibuja el de Publicaciones, que es real (se cuenta
// sobre GET /api/posts). Destacadas y Me gusta no tienen endpoint: mostrar un
// número —incluido un 0— afirmaría un dato que nadie ha consultado. El panel
// de cada una explica su estado.
//
// Patrón ARIA completo: role=tablist/tab/tabpanel, aria-selected, tabindex
// móvil y navegación con flechas/Home/End. La sección activa vive en la URL
// (?tab=) para poder compartir y recargar el perfil en la misma pestaña.

export const PROFILE_TABS = [
  { id: "posts", label: "Publicaciones", icon: "grid_view", counted: true },
  { id: "featured", label: "Destacadas", icon: "star", counted: false },
  { id: "likes", label: "Me gusta", icon: "favorite", counted: false },
];

export const DEFAULT_TAB = PROFILE_TABS[0].id;

export function isProfileTab(value) {
  return PROFILE_TABS.some((tab) => tab.id === value);
}

export default function ProfileTabs({ active, onChange, counts = {} }) {
  const refs = useRef({});

  const focusTab = (id) => {
    onChange(id);
    refs.current[id]?.focus();
  };

  const handleKeyDown = (event) => {
    const index = PROFILE_TABS.findIndex((tab) => tab.id === active);
    if (index === -1) return;

    const last = PROFILE_TABS.length - 1;
    let next = null;

    if (event.key === "ArrowRight") next = index === last ? 0 : index + 1;
    else if (event.key === "ArrowLeft") next = index === 0 ? last : index - 1;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = last;

    if (next === null) return;
    event.preventDefault();
    focusTab(PROFILE_TABS[next].id);
  };

  return (
    <div
      role="tablist"
      aria-label="Secciones del perfil"
      onKeyDown={handleKeyDown}
      className="th-scrollbar-none flex gap-1 overflow-x-auto border-b border-th-border"
    >
      {PROFILE_TABS.map(({ id, label, counted }) => {
        const selected = id === active;
        return (
          <button
            key={id}
            ref={(node) => {
              refs.current[id] = node;
            }}
            type="button"
            role="tab"
            id={`profile-tab-${id}`}
            aria-selected={selected}
            aria-controls={`profile-panel-${id}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(id)}
            className={`relative flex min-h-[48px] shrink-0 items-center gap-2 whitespace-nowrap border-b-2 px-4 text-label-lg transition-colors th-focus-ring ${
              selected
                ? "border-th-brand font-bold text-th-brand-fg"
                : "border-transparent font-semibold text-th-fg-muted hover:text-th-fg-strong"
            }`}
          >
            {label}
            {counted && (
              <span
                className={`rounded-th-pill px-2 py-0.5 text-label-md font-bold tabular-nums ${
                  selected
                    ? "bg-th-brand-soft-strong text-th-brand-fg"
                    : "bg-th-surface-raised text-th-fg-muted"
                }`}
              >
                {(counts[id] ?? 0).toLocaleString("es")}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
