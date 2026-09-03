import { NavLink } from "react-router-dom";
import {
  IoSparklesOutline,
  IoSearchOutline,
  IoCompassOutline,
  IoNotificationsOutline,
  IoPersonOutline,
  IoAddOutline,
} from "react-icons/io5";
import { useLanguage } from "@shared/i18n";

export default function MobileNav({ onOpenComposer, onOpenSearch, unreadCount = 0 }) {
  const { t } = useLanguage();

  const ITEMS = [
    { to: "/feed", label: t("nav.home"), icon: IoSparklesOutline },
    { to: "__search__", label: t("nav.search"), icon: IoSearchOutline },
    { to: "/discover", label: t("nav.discover"), icon: IoCompassOutline },
    { to: "__create__", label: t("nav.createCapsule"), icon: IoAddOutline },
    { to: "/notifications", label: t("nav.notifications"), icon: IoNotificationsOutline },
    { to: "/profile", label: t("nav.profile"), icon: IoPersonOutline },
  ];

  return (
    <nav
      aria-label={t("nav.ariaMain")}
      className="lg:hidden fixed bottom-4 inset-x-4 z-40 flex items-center justify-around bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-full shadow-lift py-2 px-2"
    >
      {ITEMS.map(({ to, label, icon: Icon }) =>
        to === "__create__" ? (
          <button
            key={to}
            onClick={onOpenComposer}
            aria-label={label}
            className="flex items-center justify-center w-12 h-12 -mt-6 rounded-full bg-ink dark:bg-ink-dark text-surface dark:text-surface-dark shadow-lift active:scale-95 transition-transform"
          >
            <Icon size={24} />
          </button>
        ) : to === "__search__" ? (
          <button
            key={to}
            onClick={onOpenSearch}
            aria-label={label}
            className="flex items-center justify-center w-11 h-11 rounded-full text-muted dark:text-muted-dark transition"
          >
            <Icon size={22} />
          </button>
        ) : (
          <NavLink
            key={to}
            to={to}
            aria-label={to === "/notifications" && unreadCount > 0 ? t("nav.notificationsUnread", { count: unreadCount }) : label}
            className={({ isActive }) =>
              `relative flex items-center justify-center w-11 h-11 rounded-full transition ${
                isActive ? "bg-line dark:bg-line-dark text-ink dark:text-ink-dark" : "text-muted dark:text-muted-dark"
              }`
            }
          >
            <Icon size={22} />
            {to === "/notifications" && unreadCount > 0 && (
              <span className="absolute top-1.5 right-2 w-2 h-2 rounded-full bg-ember-500" />
            )}
          </NavLink>
        )
      )}
    </nav>
  );
}
