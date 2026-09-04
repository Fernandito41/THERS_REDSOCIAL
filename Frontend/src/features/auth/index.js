export { default as AuthPage } from "./pages/AuthPage";
export { default as Login } from "./pages/Login";
export { default as Register } from "./pages/Register";
export { default as ForgotPassword } from "./pages/ForgotPassword";
export { default as ResetPassword } from "./pages/ResetPassword";
export { AuthProvider, useAuth, getStoredToken } from "./context/AuthContext";
export { useOAuthNotice } from "./hooks/useOAuthNotice";
// Regla de username reutilizada fuera de auth (Perfil: EditProfileModal) para
// no duplicar el mismo regex -- refleja la política que valida el backend en
// PATCH /api/users/me (ADR-003).
export { isValidUsername } from "./lib/validators";