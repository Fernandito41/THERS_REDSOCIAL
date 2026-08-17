import { useOutletContext, useNavigate, Link } from "react-router-dom";
import { IoSunnyOutline, IoMoonOutline, IoLogOutOutline, IoPersonOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { useAuth } from "@features/auth";

export default function Settings() {
  // theme/toggleTheme vienen del contexto de AppShell (única fuente de verdad)
  // -- tener una segunda instancia de useTheme() aquí desincronizaba el estado
  // mostrado en esta página del que se ve en el menú del avatar.
  const { currentUser, theme, toggleTheme } = useOutletContext();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-extrabold tracking-tight text-ink dark:text-ink-dark">Configuración</h1>

      <section className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
        <h2 className="text-sm font-semibold text-ink dark:text-ink-dark mb-4">Cuenta</h2>

        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Avatar name={currentUser.name} size="w-12 h-12" />
            <div className="min-w-0">
              <p className="text-ink dark:text-ink-dark font-medium truncate">{currentUser.name}</p>
              <p className="text-muted text-sm truncate">@{currentUser.username}</p>
              {currentUser.email && <p className="text-muted text-xs truncate">{currentUser.email}</p>}
            </div>
          </div>

          <Link
            to="/profile"
            className="shrink-0 flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
          >
            <IoPersonOutline size={14} /> Editar perfil
          </Link>
        </div>
      </section>

      <section className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
        <h2 className="text-sm font-semibold text-ink dark:text-ink-dark mb-4">Apariencia</h2>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-ink dark:text-ink-dark">Tema</p>
            <p className="text-muted text-xs">
              {theme === "dark" ? "Modo oscuro activado" : "Modo claro activado"}
            </p>
          </div>

          <button
            onClick={toggleTheme}
            className="flex items-center gap-2 text-xs font-semibold px-3 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
          >
            {theme === "dark" ? <IoSunnyOutline size={15} /> : <IoMoonOutline size={15} />}
            Cambiar a {theme === "dark" ? "claro" : "oscuro"}
          </button>
        </div>
      </section>

      <section className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
        <h2 className="text-sm font-semibold text-ink dark:text-ink-dark mb-2">Privacidad y seguridad</h2>
        <p className="text-muted text-sm">
          Todavía no hay backend para gestionar contraseña, sesiones activas ni privacidad de la cuenta
          — esta sección queda pendiente hasta que exista esa API.
        </p>
      </section>

      <button
        onClick={handleLogout}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-ember-600 border border-ember-600/30 hover:bg-ember-50 dark:hover:bg-ember-900/10 transition"
      >
        <IoLogOutOutline size={18} /> Cerrar sesión
      </button>
    </div>
  );
}
