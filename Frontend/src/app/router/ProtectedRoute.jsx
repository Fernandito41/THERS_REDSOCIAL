import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@features/auth";
import Spinner from "@shared/components/Spinner";

// Única fuente de verdad para decidir si una rama de rutas requiere sesión --
// consulta el estado centralizado de AuthProvider (nunca localStorage
// directamente), para no duplicar la lógica de autenticación que antes vivía
// dentro de AppShell.jsx.
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

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

  return <Outlet />;
}
