import { useEffect, useId, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  IoArrowBack,
  IoEllipsisVertical,
  IoLinkOutline,
  IoNotificationsOutline,
  IoSearchOutline,
  IoSettingsOutline,
} from "react-icons/io5";

// Barra superior de la tarjeta de perfil (Frontend/src/assets/ideas_perfil.jpeg):
// volver a la izquierda y los tres controles de la derecha -- buscar,
// notificaciones y menú de más acciones.
//
// Los tres hacen algo real: buscar lleva a Explorar, la campana a
// Notificaciones (con su punto de no leídas) y el menú abre acciones que ya
// existen. No hay botones decorativos.

export default function ProfileTopBar({ onOpenSearch, onCopyLink, unreadCount = 0 }) {
  const navigate = useNavigate();
  const uid = useId();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    if (!menuOpen) return undefined;

    const onPointerDown = (event) => {
      if (menuRef.current?.contains(event.target) || triggerRef.current?.contains(event.target)) return;
      setMenuOpen(false);
    };

    const onKeyDown = (event) => {
      if (event.key !== "Escape") return;
      setMenuOpen(false);
      // El foco vuelve al botón que abrió el menú, no al principio del documento.
      triggerRef.current?.focus();
    };

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [menuOpen]);

  const iconButton =
    "flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-ink transition hover:bg-canvas active:scale-95 dark:text-ink-dark dark:hover:bg-canvas-dark";

  const menuItem =
    "flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-sm text-ink transition hover:bg-canvas dark:text-ink-dark dark:hover:bg-canvas-dark";

  return (
    <div className="flex items-center justify-between gap-2 px-3 py-2.5">
      <button
        type="button"
        onClick={() => navigate(-1)}
        aria-label="Volver"
        className={iconButton}
      >
        <IoArrowBack size={21} aria-hidden="true" />
      </button>

      <div className="flex items-center gap-0.5">
        <button type="button" onClick={onOpenSearch} aria-label="Buscar en THERS" className={iconButton}>
          <IoSearchOutline size={20} aria-hidden="true" />
        </button>

        <Link
          to="/notifications"
          aria-label={
            unreadCount > 0 ? `Notificaciones, ${unreadCount} sin leer` : "Notificaciones"
          }
          className={`relative ${iconButton}`}
        >
          <IoNotificationsOutline size={20} aria-hidden="true" />
          {unreadCount > 0 && (
            <span
              aria-hidden="true"
              className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-ember-500 ring-2 ring-surface dark:ring-surface-dark"
            />
          )}
        </Link>

        <div className="relative">
          <button
            ref={triggerRef}
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-label="Más acciones"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            aria-controls={menuOpen ? `${uid}-menu` : undefined}
            className={iconButton}
          >
            <IoEllipsisVertical size={20} aria-hidden="true" />
          </button>

          {menuOpen && (
            <div
              ref={menuRef}
              id={`${uid}-menu`}
              role="menu"
              className="animate-float-in absolute right-0 top-12 z-20 w-56 overflow-hidden rounded-2xl border border-line bg-surface py-1.5 shadow-lift motion-reduce:animate-none dark:border-line-dark dark:bg-surface-dark"
            >
              <button
                type="button"
                role="menuitem"
                onClick={() => {
                  setMenuOpen(false);
                  onCopyLink();
                }}
                className={menuItem}
              >
                <IoLinkOutline size={17} aria-hidden="true" /> Copiar enlace del perfil
              </button>

              <Link to="/settings" role="menuitem" onClick={() => setMenuOpen(false)} className={menuItem}>
                <IoSettingsOutline size={17} aria-hidden="true" /> Configuración
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
