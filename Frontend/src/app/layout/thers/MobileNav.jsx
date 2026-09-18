import { NavLink } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { useLanguage } from "@shared/i18n";
import { PRIMARY_NAV, MOBILE_NAV_IDS } from "./navigation";

/**
 * Bottom-nav móvil.
 *
 * ADAPTACIÓN NUEVA, no reproducción de un diseño recibido: las 24 capturas
 * son de escritorio y ninguna muestra navegación móvil
 * (docs/THERS_REFERENCE_MANIFEST.md §4.3).
 *
 * Sigue el criterio del archivo maestro §6.2: un conjunto manejable de
 * destinos primarios, con el resto accesible desde el drawer y el perfil.
 * Respeta safe-area para no quedar bajo el gesto del sistema.
 */
export default function MobileNav({ unreadMessages = 0, hasUnreadNotifications = false, onCreate }) {
  const { t } = useLanguage();

  const items = MOBILE_NAV_IDS.map((id) =>
    id === "__create__" ? { id } : PRIMARY_NAV.find((item) => item.id === id)
  ).filter(Boolean);

  return (
    <nav
      aria-label={t("nav.ariaMobile")}
      className="fixed inset-x-0 bottom-0 z-th-nav flex items-center justify-around border-t border-th-border bg-th-surface-translucent pb-[env(safe-area-inset-bottom)] backdrop-blur-xl lg:hidden"
      style={{ minHeight: "var(--th-bottomnav-h)" }}
    >
      {items.map((item) =>
        item.id === "__create__" ? (
          <button
            key="create"
            type="button"
            onClick={onCreate}
            aria-label={t("nav.create")}
            className="flex h-12 w-12 items-center justify-center rounded-th-pill bg-th-brand text-th-on-brand shadow-th-compose transition-transform th-focus-ring active:scale-95"
          >
            <Icon name="add" size={24} />
          </button>
        ) : (
          <NavLink
            key={item.id}
            to={item.to}
            aria-label={
              item.id === "messages" && unreadMessages > 0
                ? t("nav.messagesUnread", { count: unreadMessages })
                : t(item.labelKey)
            }
            /* Zona táctil de 44x44 mínimo (archivo maestro §12) aunque el
               icono se dibuje a 24px. */
            className={({ isActive }) =>
              `relative flex min-h-[44px] min-w-[44px] flex-1 flex-col items-center justify-center gap-0.5 py-2 transition-colors th-focus-ring ${
                isActive ? "text-th-brand" : "text-th-fg-muted"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className="relative">
                  <Icon name={item.icon} size={24} fill={isActive ? 1 : 0} />
                  {item.id === "messages" && unreadMessages > 0 && (
                    <span className="absolute -right-2 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-th-pill bg-th-brand px-1 text-[10px] font-bold text-th-on-brand">
                      {unreadMessages > 9 ? "9+" : unreadMessages}
                    </span>
                  )}
                  {item.id === "notifications" && hasUnreadNotifications && (
                    <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-th-pill bg-th-danger-accent" />
                  )}
                </span>
                <span className="text-label-sm font-semibold">{t(item.labelKey)}</span>
              </>
            )}
          </NavLink>
        )
      )}
    </nav>
  );
}
