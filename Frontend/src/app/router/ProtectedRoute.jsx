import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@features/auth";
import Spinner from "@shared/components/Spinner";

const COMPLETE_PROFILE_PATH = "/complete-profile";

// Única fuente de verdad para decidir si una rama de rutas requiere sesión --
// consulta el estado centralizado de AuthProvider (nunca localStorage
// directamente), para no duplicar la lógica de autenticación que antes vivía
// dentro de AppShell.jsx.
//
// ADR-012-google-sign-in.md §Decisión (FASE 18): una cuenta con
// `profile_completed=false` (creada vía "Continuar con Google", perfil sin
// completar todavía) tiene sesión válida pero se redirige a
// /complete-profile antes de llegar a cualquier otra ruta protegida --
// mismo patrón que ya usa `email_verified` en Login.jsx, pero decidido acá
// (una sola vez, para toda la rama protegida) en vez de en cada página. El
// propio backend controla el estado real (`user.profile_completed` viene de
// PATCH/GET /api/users/me) -- nunca se puede "saltar" este paso navegando
// directo a otra URL protegida.
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-canvas dark:bg-canvas-dark">
        <Spinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.profile_completed === false && location.pathname !== COMPLETE_PROFILE_PATH) {
    return <Navigate to={COMPLETE_PROFILE_PATH} replace />;
  }

  return <Outlet />;
}
