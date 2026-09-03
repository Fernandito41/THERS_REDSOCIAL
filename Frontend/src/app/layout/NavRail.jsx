import { NavLink } from "react-router-dom";
import {
  IoSparklesOutline,
  IoSearchOutline,
  IoCompassOutline,
  IoChatbubbleEllipsesOutline,
  IoNotificationsOutline,
  IoPersonOutline,
  IoSettingsOutline,
  IoAddOutline,
} from "react-icons/io5";
import { useLanguage } from "@shared/i18n";

// Rail de navegación con la identidad monocroma de THERS
// (Frontend/src/assets/ideas_perfil.jpeg): ícono + etiqueta visible en cada
// destino y la sección activa marcada con un bloque neutro, no con el morado
// de marca. Las etiquetas dejaron de ser tooltips en hover: un menú solo de
// íconos es más difícil de descubrir, y el hover no existe en táctil.

export default function NavRail({ onOpenComposer, onOpenSearch, unreadCount = 0 }) {
  const { t } = useLanguage();

  const ITEMS = [
    { to: "/feed", label: t("nav.home"), icon: IoSparklesOutline },
    { to: "/discover", label: t("nav.discover"), icon: IoCompassOutline },
    { to: "/messages", label: t("nav.messages"), icon: IoChatbubbleEllipsesOutline },
    { to: "/notifications", label: t("nav.notifications"), icon: IoNotificationsOutline },
    { to: "/profile", label: t("nav.profile"), icon: IoPersonOutline },
    { to: "/settings", label: t("nav.settings"), icon: IoSettingsOutline },
  ];

  const itemBase =
    "group relative flex w-full flex-col items-center justify-center gap-1 rounded-2xl py-2.5 transition";

  return (
    <nav
      aria-label={t("nav.ariaMain")}
      className="sticky top-24 hidden w-24 shrink-0 flex-col items-center gap-1 self-start rounded-[28px] border border-line bg-surface p-3 shadow-soft dark:border-line-dark dark:bg-surface-dark lg:flex"
    >
      <button
        onClick={onOpenSearch}
        aria-label={t("nav.search")}
        className={`${itemBase} cursor-pointer text-muted hover:bg-canvas hover:text-ink dark:text-muted-dark dark:hover:bg-canvas-dark dark:hover:text-ink-dark`}
      >
        <IoSearchOutline size={22} aria-hidden="true" />
        <span className="text-[10px] font-medium leading-none">{t("nav.search")}</span>
      </button>

      {ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          aria-label={
            to === "/notifications" && unreadCount > 0
              ? t("nav.notificationsUnread", { count: unreadCount })
              : label
          }
          className={({ isActive }) =>
            `${itemBase} ${
              isActive
                ? "bg-line font-semibold text-ink dark:bg-line-dark dark:text-ink-dark"
                : "font-medium text-muted hover:bg-canvas hover:text-ink dark:text-muted-dark dark:hover:bg-canvas-dark dark:hover:text-ink-dark"
            }`
          }
        >
          <span className="relative">
            <Icon size={22} aria-hidden="true" />
            {to === "/notifications" && unreadCount > 0 && (
              <span
                aria-hidden="true"
                className="absolute -right-1 -top-0.5 h-2 w-2 rounded-full bg-ember-500"
              />
            )}
          </span>
          <span className="text-[10px] leading-none">{label}</span>
        </NavLink>
      ))}

      <button
        onClick={onOpenComposer}
        aria-label={t("nav.createCapsule")}
        className="mt-3 flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-2xl bg-ink py-3 text-xs font-semibold text-surface shadow-soft transition hover:opacity-90 active:scale-95 dark:bg-ink-dark dark:text-surface-dark"
      >
        <IoAddOutline size={18} aria-hidden="true" />
        Crear
      </button>
    </nav>
  );
}
