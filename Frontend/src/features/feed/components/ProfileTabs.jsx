import { useRef } from "react";
import {
  IoBookmarkOutline,
  IoChatbubbleOutline,
  IoGridOutline,
  IoHeartOutline,
  IoImagesOutline,
} from "react-icons/io5";

// Barra de secciones del perfil (identidad de referencia:
// Frontend/src/assets/ideas_perfil.jpeg). Patrón ARIA de tabs completo:
// role=tablist/tab/tabpanel, aria-selected, tabindex móvil y navegación con
// flechas/Home/End -- no basta con `aria-selected` sobre botones sueltos.
// La sección activa vive en la URL (?tab=), así que un perfil abierto en
// "Guardados" se puede compartir y recargar sin perder el estado.

export const PROFILE_TABS = [
  { id: "posts", label: "Publicaciones", Icon: IoGridOutline },
  { id: "replies", label: "Respuestas", Icon: IoChatbubbleOutline },
  { id: "media", label: "Media", Icon: IoImagesOutline },
  { id: "saved", label: "Guardados", Icon: IoBookmarkOutline },
  { id: "likes", label: "Me gusta", Icon: IoHeartOutline },
];

export const DEFAULT_TAB = PROFILE_TABS[0].id;

export function isProfileTab(value) {
  return PROFILE_TABS.some((tab) => tab.id === value);
}

export default function ProfileTabs({ active, onChange }) {
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
      className="no-scrollbar flex gap-1 overflow-x-auto border-t border-line px-2 dark:border-line-dark"
    >
      {PROFILE_TABS.map(({ id, label, Icon }) => {
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
            className={`relative flex h-12 shrink-0 cursor-pointer items-center gap-2 whitespace-nowrap px-3.5 text-sm transition-colors sm:px-4 ${
              selected
                ? "font-semibold text-ink dark:text-ink-dark"
                : "font-medium text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark"
            }`}
          >
            <Icon size={17} aria-hidden="true" />
            {label}
            {/* Indicador de sección activa: además del color, un subrayado --
                el color por sí solo no puede ser el único indicador. */}
            <span
              aria-hidden="true"
              className={`absolute inset-x-2 bottom-0 h-[3px] rounded-full bg-ink transition-opacity dark:bg-ink-dark ${
                selected ? "opacity-100" : "opacity-0"
              }`}
            />
          </button>
        );
      })}
    </div>
  );
}
