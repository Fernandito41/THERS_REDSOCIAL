import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import MobileNav from "./MobileNav";
import MobileDrawer from "./MobileDrawer";

/**
 * Armazón visual del shell: sidebar + topbar + área de contenido + navegación
 * móvil. Solo presentación — no obtiene datos ni conoce la API.
 *
 * Existe para que haya UNA sola implementación del shell (archivo maestro
 * §3.1: "nunca tres copias independientes de su implementación"). Lo consumen:
 *   · AppShell — la aplicación real, que le pasa datos de sesión y API.
 *   · El harness de QA visual (src/dev/qa) — que le pasa fixtures
 *     deterministas para poder comparar contra las capturas de referencia sin
 *     depender del backend.
 *
 * `variant` resuelve los tokens de tokens.css vía `data-th-shell`: 288px y
 * neutrales slate para lo social, 256px y Luminous para Configuración y
 * Mensajes (docs/THERS_REFERENCE_MANIFEST.md §5).
 */
export default function ShellFrame({
  variant = "social",
  currentUser,
  unreadMessages = 0,
  hasUnreadNotifications = false,
  onCreate,
  onLogout,
  theme,
  onToggleTheme,
  drawerOpen = false,
  onOpenDrawer,
  onCloseDrawer,
  children,
}) {
  const sidebarProps = {
    currentUser,
    unreadMessages,
    hasUnreadNotifications,
    onCreate,
  };

  return (
    <div
      data-th-shell={variant}
      className="min-h-screen bg-th-bg font-jakarta text-th-fg antialiased"
    >
      <Sidebar {...sidebarProps} />

      <MobileDrawer open={drawerOpen} onClose={onCloseDrawer} {...sidebarProps} />

      <Topbar
        currentUser={currentUser}
        hasUnreadNotifications={hasUnreadNotifications}
        onOpenMobileNav={onOpenDrawer}
        onLogout={onLogout}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />

      {/* El desplazamiento usa la MISMA variable que el ancho de la sidebar
          (--th-sidebar-w), así que header, sidebar y contenido no pueden
          descuadrarse entre variantes (archivo maestro §6.1). */}
      <div className="lg:pl-th-sidebar">
        <main
          id="main"
          className="min-h-screen px-4 pb-[calc(var(--th-bottomnav-h)+env(safe-area-inset-bottom)+16px)] pt-[calc(var(--th-topbar-h)+16px)] lg:px-th-gutter lg:pb-th-margin"
        >
          {children}
        </main>
      </div>

      <MobileNav
        unreadMessages={unreadMessages}
        hasUnreadNotifications={hasUnreadNotifications}
        onCreate={onCreate}
      />
    </div>
  );
}
