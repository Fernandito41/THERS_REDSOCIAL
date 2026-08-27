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

  return (
    <nav
      aria-label={t("nav.ariaMain")}
      className="hidden lg:flex flex-col items-center gap-1 w-20 shrink-0 sticky top-24 self-start bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft py-5"
    >
      <button
        onClick={onOpenSearch}
        title={t("nav.search")}
        aria-label={t("nav.search")}
        className="group relative flex items-center justify-center w-12 h-12 rounded-2xl mb-1 text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark hover:text-ink dark:hover:text-ink-dark transition"
      >
        <IoSearchOutline size={22} />
        <span className="pointer-events-none absolute left-full ml-3 whitespace-nowrap rounded-lg bg-ink text-white text-xs font-medium px-2.5 py-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
          {t("nav.search")}
        </span>
      </button>

      {ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          title={label}
          aria-label={to === "/notifications" && unreadCount > 0 ? t("nav.notificationsUnread", { count: unreadCount }) : label}
          className={({ isActive }) =>
            `group relative flex items-center justify-center w-12 h-12 rounded-2xl mb-1 transition ${
              isActive
                ? "bg-pulse-600 text-white shadow-glow"
                : "text-muted dark:text-muted-dark hover:bg-canvas dark:hover:bg-canvas-dark hover:text-ink dark:hover:text-ink-dark"
            }`
          }
        >
          <Icon size={22} />
          {to === "/notifications" && unreadCount > 0 && (
            <span className="absolute top-1.5 right-2.5 w-2 h-2 rounded-full bg-ember-500" />
          )}
          <span className="pointer-events-none absolute left-full ml-3 whitespace-nowrap rounded-lg bg-ink text-white text-xs font-medium px-2.5 py-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            {label}
          </span>
        </NavLink>
      ))}

      <button
        onClick={onOpenComposer}
        title={t("nav.createCapsule")}
        aria-label={t("nav.createCapsule")}
        className="mt-3 flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-pulse-500 to-pulse-700 text-white shadow-lift hover:scale-105 active:scale-95 transition-transform"
      >
        <IoAddOutline size={24} />
      </button>
    </nav>
  );
}
