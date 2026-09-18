import { NavLink, Link } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { useLanguage } from "@shared/i18n";
import { PRIMARY_NAV } from "./navigation";

/**
 * Sidebar global de THERS.
 *
 * Composición tomada de REF-FEED-01 y verificada idéntica en las 24
 * referencias: marca THERS arriba, nav de 7 destinos, botón "+ Crear" y,
 * abajo, la tarjeta de usuario con acceso a Configuración.
 *
 * ANCHO: no se fija aquí. Lo aporta `--th-sidebar-w`, que cambia con la
 * variante de shell (288px social / 256px configuración y mensajes). El
 * header y el contenido usan ESA MISMA variable, así que nunca pueden
 * descuadrarse entre sí (archivo maestro §6.1).
 *
 * La marca se dibuja como aparece en la referencia: la palabra THERS en
 * mayúsculas, sin isotipo ni badge inventados. El badge "ALPHA" de algunas
 * maquetas NO se reproduce: es un estado de producto que este repositorio no
 * declara (manifest §6).
 */
export default function Sidebar({
  currentUser,
  unreadMessages = 0,
  hasUnreadNotifications = false,
  onCreate,
  /* `asDrawer` solo cambia el posicionamiento del contenedor. El contenido es
     el mismo en escritorio y en el drawer móvil: una sola implementación de
     la navegación, no dos copias (archivo maestro §3.1). */
  asDrawer = false,
  onNavigate,
}) {
  const { t } = useLanguage();

  const itemBase =
    "group flex items-center justify-between gap-3 rounded-th-input px-4 py-2.5 text-label-lg transition-colors th-focus-ring";

  return (
    <aside
      onClick={asDrawer ? (event) => event.target.closest("a") && onNavigate?.() : undefined}
      className={
        asDrawer
          ? "flex h-full w-[min(88vw,320px)] flex-col justify-between overflow-y-auto border-r border-th-border bg-th-surface p-4"
          : "fixed inset-y-0 left-0 z-th-nav hidden w-th-sidebar flex-col justify-between border-r border-th-border bg-th-surface p-4 shadow-th-card lg:flex"
      }
      aria-label={t("nav.ariaMain")}
    >
      <div className="flex min-h-0 flex-col gap-6">
        <div className="flex items-center justify-between px-2 pt-1">
          <Link to="/feed" className="rounded-th-sm th-focus-ring">
            <span className="font-jakarta text-headline-md font-extrabold uppercase tracking-tight text-th-fg-strong">
              THERS
            </span>
          </Link>
        </div>

        <nav className="flex min-h-0 flex-col gap-1 overflow-y-auto" aria-label={t("nav.ariaPrimary")}>
          {PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.id}
              to={item.to}
              className={({ isActive }) =>
                `${itemBase} ${
                  isActive
                    ? "bg-th-brand-soft font-bold text-th-brand-fg shadow-th-card"
                    : "text-th-fg-muted hover:bg-th-surface-raised hover:text-th-fg-strong"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span className="flex min-w-0 items-center gap-4">
                    <Icon
                      name={item.icon}
                      size={24}
                      fill={isActive ? 1 : 0}
                      className={
                        isActive
                          ? "text-th-brand"
                          : "text-th-fg-subtle transition-colors group-hover:text-th-brand"
                      }
                    />
                    <span className="truncate">{t(item.labelKey)}</span>
                  </span>

                  {/* Los indicadores solo se dibujan con un valor real.
                      El "4" y el "LIVE" de la maqueta son muestra. */}
                  {item.badge === "count" && unreadMessages > 0 && (
                    <span className="flex h-5 min-w-[20px] items-center justify-center rounded-th-pill bg-th-brand-soft-strong px-1.5 text-label-sm font-bold text-th-brand-fg">
                      {unreadMessages > 99 ? "99+" : unreadMessages}
                    </span>
                  )}
                  {item.badge === "dot" && hasUnreadNotifications && (
                    <span
                      className="h-2 w-2 shrink-0 rounded-th-pill bg-th-danger-accent"
                      aria-label={t("nav.hasUnread")}
                      role="status"
                    />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="pt-1">
          <button
            type="button"
            onClick={onCreate}
            className="flex w-full items-center justify-center gap-2 rounded-th-pill bg-th-brand px-6 py-2.5 text-label-lg font-bold text-th-on-brand shadow-th-card transition-colors th-focus-ring hover:bg-th-brand-hover active:scale-[0.98]"
          >
            <Icon name="add" size={20} />
            <span>{t("nav.create")}</span>
          </button>
        </div>
      </div>

      {/* Tarjeta de sesión. La identidad sale SIEMPRE de la sesión real, nunca
          de "Cristopher Stanley" ni de ninguna persona de las muestras
          (archivo maestro §10, manifest §6). */}
      <div className="flex items-center justify-between gap-2 rounded-th-card border border-th-border bg-th-surface-subtle p-2 transition-colors hover:bg-th-surface-raised">
        <Link
          to="/profile"
          className="flex min-w-0 items-center gap-2 rounded-th-sm th-focus-ring"
        >
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-th-pill bg-th-brand text-headline-sm font-bold text-th-on-brand">
            {initialsOf(currentUser)}
          </span>
          <span className="flex min-w-0 flex-col">
            <span className="truncate text-label-md font-semibold text-th-fg-strong">
              {currentUser?.name}
            </span>
            <span className="truncate text-body-sm text-th-fg-muted">@{currentUser?.username}</span>
          </span>
        </Link>

        <Link
          to="/settings"
          aria-label={t("nav.settings")}
          className="rounded-th-sm p-1 text-th-fg-subtle transition-colors th-focus-ring hover:bg-th-surface hover:text-th-fg-strong"
        >
          <Icon name="settings" size={20} />
        </Link>
      </div>
    </aside>
  );
}

function initialsOf(user) {
  const source = user?.name || user?.username || "";
  const parts = source.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
