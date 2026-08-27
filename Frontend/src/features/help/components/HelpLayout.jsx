import { Outlet, Link, useNavigate } from "react-router-dom";
import { IoArrowBackOutline } from "react-icons/io5";
import { useAuth } from "@features/auth";
import HelpSidebar from "./HelpSidebar";
import HelpMobileCategoryNav from "./HelpMobileCategoryNav";
import HelpSearchBar from "./HelpSearchBar";
import { HelpAssistantPanel, HelpAssistantFloatingButton } from "./HelpAssistant";

// Envuelve todas las rutas /help/* (ya anidadas dentro de PublicLayout, que
// aporta el header/footer compartidos de THERS -- ver app/router/router.jsx).
// Acá solo se agrega lo propio del Centro de Ayuda: la etiqueta "Centro de
// Ayuda", el acceso de vuelta al producto (según haya o no sesión), el
// buscador persistente y el layout de tres columnas (categorías | contenido
// | asistente) que se adapta a un stack de una sola columna en mobile.
export default function HelpLayout() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const backTo = isAuthenticated ? "/feed" : "/";
  const backLabel = isAuthenticated ? "Volver a THERS" : "Volver al inicio";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <button
            type="button"
            onClick={() => navigate(backTo)}
            className="inline-flex items-center gap-1.5 text-sm text-muted dark:text-muted-dark hover:text-ink dark:hover:text-ink-dark transition-colors"
          >
            <IoArrowBackOutline size={15} aria-hidden="true" />
            {backLabel}
          </button>
          <h1 className="mt-1 text-xl sm:text-2xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
            <Link to="/help" className="hover:text-pulse-600 dark:hover:text-pulse-300 transition-colors">
              Centro de Ayuda
            </Link>
          </h1>
        </div>

        <div className="hidden sm:block w-72">
          <HelpSearchBar size="sm" placeholder="Buscar en el Centro de Ayuda..." />
        </div>
      </div>

      <div className="sm:hidden mb-6">
        <HelpSearchBar size="sm" />
      </div>

      <div className="mb-6">
        <HelpMobileCategoryNav />
      </div>

      <div className="flex items-start gap-6">
        <HelpSidebar />

        <main className="flex-1 min-w-0">
          <Outlet />
        </main>

        <HelpAssistantPanel />
      </div>

      <HelpAssistantFloatingButton />
    </div>
  );
}
