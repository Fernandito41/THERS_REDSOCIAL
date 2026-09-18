import { useEffect, useMemo, useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useTheme } from "@shared/hooks/useTheme";
import { useLanguage } from "@shared/i18n";
import { useAuth, getStoredToken } from "@features/auth";
import { api, getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import ShellFrame from "./thers/ShellFrame";
import { shellVariantFor } from "./thers/navigation";
import CreateCapsuleFlow from "@features/feed/components/CreateCapsuleFlow";
import { mapNotification } from "@features/feed/lib/mapNotification";

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

export default function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
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
  // `notifications` = notificaciones reales (GET /api/notifications,
  // ADR-008-notifications-minimal-model.md) -- ya no mockNotifications.
  const [notifications, setNotifications] = useState([]);
  const [isComposerOpen, setComposerOpen] = useState(false);
  // El drawer de navegación móvil sustituye al buscador/menú desplegable que
  // antes vivían en el header: ahora el buscador es un formulario real del
  // Topbar y el menú de perfil se gobierna dentro de ese componente.
  const [drawerOpen, setDrawerOpen] = useState(false);

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

    // GET /api/notifications (ADR-008). Sin estado de loading propio --
    // Notifications.jsx ya maneja bien una lista vacía mientras llega
    // (mismo criterio que unreadCount parte de [] hasta que resuelva). Un
    // error acá no bloquea el resto del shell -- se avisa por Toast, mismo
    // patrón que loadPosts.
    async function loadNotifications() {
      try {
        const res = await api.get("/notifications", { headers: authHeaders() });
        if (!cancelled) setNotifications(res.data.notifications.map(mapNotification));
      } catch (error) {
        if (!cancelled) toast.error(getErrorMessage(error, t));
      }
    }

    loadPosts();
    loadNotifications();
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

  // PATCH /api/notifications/<id>/read (ADR-008-notifications-minimal-model.md).
  // Optimistic update + rollback, mismo patrón que handleToggleLike
  // (ADR-005). Un no-op silencioso si ya estaba leída o el id no existe más
  // en el estado local -- evita una request de más al reabrir el panel.
  const handleMarkRead = async (id) => {
    const notification = notifications.find((n) => n.id === id);
    if (!notification || notification.read) return;

    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));

    try {
      await api.patch(`/notifications/${id}/read`, null, { headers: authHeaders() });
    } catch (error) {
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: false } : n)));
      toast.error(getErrorMessage(error, t));
    }
  };

  // Sin endpoint batch en el backend (ADR-008 §No objetivos) -- marca cada
  // notificación no leída individualmente, reutilizando handleMarkRead
  // (mismo optimistic update + rollback por ítem, sin duplicar esa lógica).
  const handleMarkAllRead = () => {
    notifications.filter((n) => !n.read).forEach((n) => handleMarkRead(n.id));
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

  // POST/DELETE /api/posts/<id>/like (ADR-005-likes-minimal-model.md).
  // Optimistic update -- el toggle se ve al instante; si la request falla,
  // se revierte y se avisa con el mismo patrón de error que el resto de
  // AppShell (getErrorMessage + Toast). Ambos endpoints son idempotentes
  // (ADR-005 §Decisión), así que un doble clic durante una request en vuelo
  // nunca deja el contador desincronizado.
  const handleToggleLike = async (postId) => {
    const capsule = capsules.find((c) => c.id === postId);
    if (!capsule) return;

    const wasLiked = capsule.liked_by_me;
    const previousCount = capsule.likes_count;

    setCapsules((prev) =>
      prev.map((c) =>
        c.id === postId
          ? { ...c, liked_by_me: !wasLiked, likes_count: previousCount + (wasLiked ? -1 : 1) }
          : c
      )
    );

    try {
      const res = wasLiked
        ? await api.delete(`/posts/${postId}/like`, { headers: authHeaders() })
        : await api.post(`/posts/${postId}/like`, null, { headers: authHeaders() });
      setCapsules((prev) => prev.map((c) => (c.id === postId ? { ...c, ...res.data } : c)));
    } catch (error) {
      setCapsules((prev) =>
        prev.map((c) => (c.id === postId ? { ...c, liked_by_me: wasLiked, likes_count: previousCount } : c))
      );
      toast.error(getErrorMessage(error, t));
    }
  };

  // GET /api/posts/<id>/comments (ADR-006-comments-minimal-model.md). A
  // diferencia de likes_count (que viaja con cada post), los comentarios se
  // piden bajo demanda cuando CapsuleCard abre su panel -- no tiene sentido
  // cargar el hilo completo de cada post del feed de antemano. Sin
  // try/catch acá -- CapsuleCard lo maneja (Toast + estado local del panel),
  // mismo criterio que handleCreateCapsule/CreateCapsuleFlow.
  const handleLoadComments = async (postId) => {
    const res = await api.get(`/posts/${postId}/comments`, { headers: authHeaders() });
    return res.data.comments;
  };

  // POST /api/posts/<id>/comments. El contador (`comments_count`) vive en
  // `capsules` (AppShell), no en CapsuleCard -- se actualiza acá para que
  // el número en la tarjeta quede sincronizado apenas el comentario se
  // publica, sin depender de que CapsuleCard vuelva a pedir el post entero.
  const handlePostComment = async (postId, content) => {
    const res = await api.post(
      `/posts/${postId}/comments`,
      { content },
      { headers: authHeaders() }
    );
    setCapsules((prev) =>
      prev.map((c) => (c.id === postId ? { ...c, comments_count: c.comments_count + 1 } : c))
    );
    return res.data.comment;
  };

  // POST/DELETE /api/users/<id>/follow (ADR-007-follows-minimal-model.md).
  // No reutiliza followingIds/handleToggleFollow (ese Set en memoria sigue
  // siendo exclusivo del panel de sugerencias mock de Home.jsx -- esas
  // personas no existen en el backend, llamar a este endpoint con sus ids
  // daría 404 real). Actúa sobre `author.is_followed_by_me`, que ya viaja
  // con cada post -- y actualiza TODOS los posts de ese autor en `capsules`,
  // no solo el que disparó la acción, para que el estado quede consistente
  // en toda la tarjeta del feed. Mismo patrón de optimistic update +
  // rollback que handleToggleLike (ADR-005).
  const handleToggleFollowAuthor = async (authorId) => {
    const capsule = capsules.find((c) => c.author.id === authorId);
    if (!capsule) return;

    const wasFollowing = capsule.author.is_followed_by_me;

    setCapsules((prev) =>
      prev.map((c) =>
        c.author.id === authorId
          ? { ...c, author: { ...c.author, is_followed_by_me: !wasFollowing } }
          : c
      )
    );

    try {
      wasFollowing
        ? await api.delete(`/users/${authorId}/follow`, { headers: authHeaders() })
        : await api.post(`/users/${authorId}/follow`, null, { headers: authHeaders() });
    } catch (error) {
      setCapsules((prev) =>
        prev.map((c) =>
          c.author.id === authorId
            ? { ...c, author: { ...c.author, is_followed_by_me: wasFollowing } }
            : c
        )
      );
      toast.error(getErrorMessage(error, t));
    }
  };

  // Guard defensivo, no una decisión de ruteo: ProtectedRoute ya garantiza
  // isAuthenticated antes de montar AppShell; esto solo evita un crash en el
  // instante de re-render que sigue a logout() (currentUser pasa a null un
  // tick antes de que la navegación a /login desmonte este árbol).
  if (!currentUser) return null;

  // Variante visual del shell según la ruta. Las referencias se reparten en
  // dos familias (slate/288px para lo social, luminous/256px para
  // Configuración y Mensajes) y `data-th-shell` resuelve los tokens de
  // tokens.css sin duplicar el shell (docs/THERS_REFERENCE_MANIFEST.md §5).
  const shellVariant = shellVariantFor(location.pathname);

  return (
    <ShellFrame
      variant={shellVariant}
      currentUser={currentUser}
      // Sin endpoint de mensajes todavía: no se inventa un contador.
      unreadMessages={0}
      hasUnreadNotifications={unreadCount > 0}
      onCreate={() => setComposerOpen(true)}
      onLogout={handleLogout}
      theme={theme}
      onToggleTheme={toggleTheme}
      drawerOpen={drawerOpen}
      onOpenDrawer={() => setDrawerOpen(true)}
      onCloseDrawer={() => setDrawerOpen(false)}
    >
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
          onToggleLike: handleToggleLike,
          onLoadComments: handleLoadComments,
          onPostComment: handlePostComment,
          onToggleFollowAuthor: handleToggleFollowAuthor,
        }}
      />

      {isComposerOpen && (
        <CreateCapsuleFlow
          currentUser={currentUser}
          onClose={() => setComposerOpen(false)}
          onSubmit={handleCreateCapsule}
        />
      )}
    </ShellFrame>
  );
}
