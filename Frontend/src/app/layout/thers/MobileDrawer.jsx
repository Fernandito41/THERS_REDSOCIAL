import { useEffect, useRef } from "react";
import Sidebar from "./Sidebar";
import Icon from "@shared/components/Icon";
import { useLanguage } from "@shared/i18n";

/**
 * Drawer de navegación para móvil/tablet.
 *
 * Reutiliza <Sidebar asDrawer> -- no reimplementa la navegación. Maneja foco,
 * Escape, bloqueo del fondo y retorno al disparador (archivo maestro §7.3/§12).
 */
export default function MobileDrawer({ open, onClose, ...sidebarProps }) {
  const { t } = useLanguage();
  const panelRef = useRef(null);
  const previouslyFocused = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    previouslyFocused.current = document.activeElement;
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";

    function onKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab") return;

      // Contención de foco dentro del panel.
      const focusables = panelRef.current?.querySelectorAll(
        'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusables?.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    panelRef.current?.querySelector("a, button")?.focus();

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = overflow;
      previouslyFocused.current?.focus?.();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-th-modal lg:hidden">
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={t("nav.ariaMain")}
        className="absolute inset-y-0 left-0 shadow-th-overlay"
      >
        <button
          type="button"
          onClick={onClose}
          aria-label={t("nav.closeMenu")}
          className="absolute right-2 top-3 z-10 flex h-10 w-10 items-center justify-center rounded-th-pill text-th-fg-muted th-focus-ring hover:bg-th-surface-raised"
        >
          <Icon name="close" size={22} />
        </button>
        <Sidebar asDrawer onNavigate={onClose} {...sidebarProps} />
      </div>
    </div>
  );
}
