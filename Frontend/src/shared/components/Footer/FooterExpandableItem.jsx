import { useId, useState } from "react";
import { Link } from "react-router-dom";
import {
  IoChevronDown,
  IoInformationCircleOutline,
  IoRocketOutline,
  IoPeopleOutline,
  IoShieldCheckmarkOutline,
  IoHelpBuoyOutline,
} from "react-icons/io5";
import InfoMediaTeaser from "./InfoMediaTeaser";

const ICONS = {
  info: IoInformationCircleOutline,
  "how-it-works": IoRocketOutline,
  community: IoPeopleOutline,
  security: IoShieldCheckmarkOutline,
  faq: IoHelpBuoyOutline,
};

// Ítem de footer con hijos (hoy solo "Información") -- en vez de navegar
// directo, se expande en el mismo lugar mostrando sub-opciones como pequeñas
// tarjetas. Mismo idioma visual que FooterLink (tipografía, color, foco);
// solo agrega el toggle y el panel.
export default function FooterExpandableItem({ label, items }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
        className="w-full flex items-center justify-between gap-2 text-sm text-muted dark:text-muted-dark hover:text-ink dark:hover:text-ink-dark transition-colors rounded-sm"
      >
        {label}
        <IoChevronDown
          size={14}
          className={`shrink-0 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div id={panelId} role="region" aria-label={label} className="mt-3 space-y-1.5 animate-float-in">
          {items.map((item) => {
            const Icon = ICONS[item.icon] || IoInformationCircleOutline;
            return (
              <Link
                key={item.to}
                to={item.to}
                className="group flex items-start gap-2.5 rounded-xl px-2 py-1.5 -mx-2 hover:bg-canvas dark:hover:bg-canvas-dark transition-colors"
              >
                <span className="shrink-0 mt-0.5 flex items-center justify-center w-7 h-7 rounded-full bg-pulse-50 dark:bg-pulse-900/30 text-pulse-600 dark:text-pulse-300 group-hover:scale-105 transition-transform">
                  <Icon size={14} aria-hidden="true" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm text-ink dark:text-ink-dark leading-tight">{item.label}</span>
                  <span className="block text-xs text-muted dark:text-muted-dark mt-0.5">{item.description}</span>
                </span>
              </Link>
            );
          })}

          <InfoMediaTeaser />
        </div>
      )}
    </div>
  );
}
