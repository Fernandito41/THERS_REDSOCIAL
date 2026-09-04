import { useEffect, useMemo, useState } from "react";
import { Outlet, useNavigate, Link } from "react-router-dom";
import {
  IoSearchOutline,
  IoChatbubbleEllipsesOutline,
  IoNotificationsOutline,
  IoSunnyOutline,
  IoMoonOutline,
  IoLogOutOutline,
  IoPersonOutline,
  IoSettingsOutline,
  IoHelpCircleOutline,
} from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import AmbientGlow from "@shared/components/AmbientGlow";
import LanguageSwitcher from "@shared/components/LanguageSwitcher";
import { useTheme } from "@shared/hooks/useTheme";
import { useLanguage } from "@shared/i18n";
import { useAuth, getStoredToken } from "@features/auth";
import { api, getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import NavRail from "./NavRail";
import MobileNav from "./MobileNav";
import CreateCapsuleFlow from "@features/feed/components/CreateCapsuleFlow";
import { mockNotifications } from "@features/feed/data/mockData";

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function AppShell() {
  const navigate = useNavigate();
  // AppShell ya no decide si hay sesión -- eso es responsabilidad exclusiva de
  // ProtectedRoute (app/router/ProtectedRoute.jsx), que envuelve esta rama de
  // rutas y solo renderiza AppShell cuando isAuthenticated es true. Acá solo
  // se consume el usuario ya resuelto por AuthProvider.
  const { user: currentUser, updateProfile, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { t } = useLanguage();
  const toast = useToast();

  // `capsules` = posts reales (GET/POST /api/posts, ADR-004-posts-minimal-model.md)
  // -- "Cápsula" sigue siendo el nombre de producto para un post, ya usado en
  // toda la UI (Home.jsx, Profile.jsx); ya no es mockCapsules.
  const [capsules, setCapsules] = useState([]);
  const [capsulesLoading, setCapsulesLoading] = useState(true);
  const [followingIds, setFollowingIds] = useState(() => new Set());
  const [notifications, setNotifications] = useState(mockNotifications);
  const [isComposerOpen, setComposerOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadPosts() {
      setCapsulesLoading(true);
      try {
        const res = await api.get("/posts", { headers: authHeaders() });
        if (!cancelled) setCapsules(res.data.posts);
      } catch (error) {
        if (!cancelled) toast.error(getErrorMessage(error, t));
      } finally {
        if (!cancelled) setCapsulesLoading(false);
      }
    }

    loadPosts();
    return () => {
      cancelled = true;
    };
  }, []);

  const unreadCount = useMemo(() => notifications.filter((n) => !n.read).length, [notifications]);

  const handleToggleFollow = (id) => {
    setFollowingIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleMarkRead = (id) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  // POST /api/posts (ADR-004-posts-minimal-model.md). Sin try/catch acá --
  // se propaga a CreateCapsuleFlow, que ya maneja error/loading con el mismo
  // patrón que AuthContext.updateProfile()/Profile.jsx (getErrorMessage +
  // Toast, formulario abierto para reintentar).
  const handleCreateCapsule = async (content) => {
    const res = await api.post("/posts", { content }, { headers: authHeaders() });
    setCapsules((prev) => [res.data.post, ...prev]);
    setComposerOpen(false);
  };

  // Guard defensivo, no una decisión de ruteo: ProtectedRoute ya garantiza
  // isAuthenticated antes de montar AppShell; esto solo evita un crash en el
  // instante de re-render que sigue a logout() (currentUser pasa a null un
  // tick antes de que la navegación a /login desmonte este árbol).
  if (!currentUser) return null;

  return (
    <div className="min-h-screen bg-canvas dark:bg-canvas-dark">
      <AmbientGlow />

      <header className="sticky top-0 z-30 bg-canvas/85 dark:bg-canvas-dark/85 backdrop-blur border-b border-line dark:border-line-dark">
        <div className="max-w-7xl mx-auto flex items-center gap-3 px-4 py-3">
          <Link to="/feed" className="flex items-center gap-2 shrink-0">
            <span className="font-extrabold text-xl tracking-tight text-ink dark:text-ink-dark">THERS</span>
          </Link>

          <div className="flex-1 flex justify-center">
            {searchOpen && (
              <div className="relative w-full max-w-md">
                <IoSearchOutline className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
                <input
                  autoFocus
                  type="text"
                  onBlur={() => setSearchOpen(false)}
                  placeholder={t("nav.searchPlaceholder")}
                  aria-label={t("nav.searchAria")}
                  className="w-full bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-full pl-10 pr-4 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
                />
              </div>
            )}
          </div>

          <div className="flex items-center gap-1 shrink-0">
            <Link
              to="/messages"
              aria-label={t("nav.messages")}
              className="p-2 rounded-full text-muted dark:text-muted-dark hover:bg-surface dark:hover:bg-surface-dark hover:text-ink dark:hover:text-ink-dark transition"
            >
              <IoChatbubbleEllipsesOutline size={21} />
            </Link>

            <Link
              to="/notifications"
              aria-label={unreadCount > 0 ? t("nav.notificationsUnread", { count: unreadCount }) : t("nav.notifications")}
              className="relative p-2 rounded-full text-muted dark:text-muted-dark hover:bg-surface dark:hover:bg-surface-dark hover:text-ink dark:hover:text-ink-dark transition"
            >
              <IoNotificationsOutline size={21} />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[16px] h-4 px-1 rounded-full bg-ember-500 text-white text-[10px] font-bold flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </Link>

            <div className="relative ml-1">
              <button onClick={() => setMenuOpen((prev) => !prev)} aria-label={t("nav.profileMenuAria")} title={currentUser.name}>
                <Avatar name={currentUser.name} size="w-8 h-8" />
              </button>

              {menuOpen && (
                <div className="absolute right-0 top-11 z-10 w-56 bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-2xl shadow-lift py-2 animate-float-in">
                  <div className="px-4 py-2 border-b border-line dark:border-line-dark">
                    <p className="text-sm font-semibold text-ink dark:text-ink-dark">{currentUser.name}</p>
                    <p className="text-xs text-muted">@{currentUser.username}</p>
                  </div>

                  <Link
                    to="/profile"
                    onClick={() => setMenuOpen(false)}
                    className="w-full flex items-center gap-2 text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                  >
                    <IoPersonOutline size={16} /> {t("nav.viewProfile")}
                  </Link>

                  <Link
                    to="/settings"
                    onClick={() => setMenuOpen(false)}
                    className="w-full flex items-center gap-2 text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                  >
                    <IoSettingsOutline size={16} /> {t("nav.settings")}
                  </Link>

                  <Link
                    to="/help"
                    onClick={() => setMenuOpen(false)}
                    className="w-full flex items-center gap-2 text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                  >
                    <IoHelpCircleOutline size={16} /> {t("nav.help")}
                  </Link>

                  <button
                    onClick={toggleTheme}
                    className="w-full flex items-center gap-2 text-left px-4 py-2 text-sm text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                  >
                    {theme === "dark" ? <IoSunnyOutline size={16} /> : <IoMoonOutline size={16} />}
                    {theme === "dark" ? t("nav.lightMode") : t("nav.darkMode")}
                  </button>

                  <div className="flex items-center justify-between gap-2 px-4 py-2">
                    <span className="text-sm text-ink dark:text-ink-dark">{t("language.label")}</span>
                    <LanguageSwitcher />
                  </div>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 text-left px-4 py-2 text-sm text-ember-600 hover:bg-canvas dark:hover:bg-canvas-dark border-t border-line dark:border-line-dark mt-1 pt-2"
                  >
                    <IoLogOutOutline size={16} /> {t("nav.logout")}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto flex gap-6 px-4 py-6">
        <NavRail
          onOpenComposer={() => setComposerOpen(true)}
          onOpenSearch={() => setSearchOpen(true)}
          unreadCount={unreadCount}
        />

        <main className="flex-1 min-w-0 pb-24 lg:pb-6">
          <Outlet
            context={{
              currentUser,
              capsules,
              capsulesLoading,
              followingIds,
              notifications,
              theme,
              toggleTheme,
              onToggleFollow: handleToggleFollow,
              onMarkRead: handleMarkRead,
              onMarkAllRead: handleMarkAllRead,
              onUpdateUser: updateProfile,
              onOpenComposer: () => setComposerOpen(true),
            }}
          />
        </main>
      </div>

      <MobileNav
        onOpenComposer={() => setComposerOpen(true)}
        onOpenSearch={() => setSearchOpen(true)}
        unreadCount={unreadCount}
      />

      {isComposerOpen && (
        <CreateCapsuleFlow
          currentUser={currentUser}
          onClose={() => setComposerOpen(false)}
          onSubmit={handleCreateCapsule}
        />
      )}
    </div>
  );
}
