import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@shared/lib/api";

const AuthContext = createContext(undefined);

const TOKEN_KEY = "token";
const USER_KEY = "user";

// El backend (POST /api/login, POST /api/register) solo devuelve { id, email, name } --
// API_CONTRACT.md §4.1, sin username. Se deriva de la parte local del email como valor
// real (no inventado) hasta que exista un campo username ratificado en
// DATABASE_ARCHITECTURE.md.
function withUsername(user) {
  return {
    ...user,
    username: user.username || user.email.split("@")[0],
  };
}

function readStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // TODO BACKEND: reemplazar el fallback local por GET /api/users/me cuando
  // Backend implemente el endpoint. Flujo previsto (no implementado todavía
  // porque el endpoint no existe -- API_CONTRACT.md §4.3 confirma que ningún
  // endpoint protegido existe hoy):
  //   App inicia -> AuthProvider -> loadCurrentUser() -> GET /api/users/me
  //     -> JWT válido: actualizar `user` con la respuesta del backend
  //     -> JWT inválido/expirado (401): limpiar sesión y quedar en isAuthenticated=false
  // Mientras tanto, la única fuente de verdad disponible es el usuario que
  // login() ya guardó en localStorage -- no se inventa una llamada a un
  // endpoint inexistente.
  const loadCurrentUser = async () => {
    setIsLoading(true);
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
      setUser(null);
      setIsLoading(false);
      return null;
    }

    const stored = readStoredUser();
    setUser(stored);
    setIsLoading(false);
    return stored;
  };

  useEffect(() => {
    loadCurrentUser();
  }, []);

  const login = async (data) => {
    const res = await api.post("/login", data);
    const loggedInUser = withUsername(res.data.user);

    localStorage.setItem(TOKEN_KEY, res.data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(loggedInUser));
    setUser(loggedInUser);

    return loggedInUser;
  };

  // El registro no inicia sesión (el backend no lo hace -- API_CONTRACT.md §4.1
  // solo documenta 201 con el `user` creado, sin `token`), por eso no toca el
  // estado de sesión de este contexto.
  const register = async (data) => {
    const res = await api.post("/register", data);
    return res.data.user;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  };

  // Edición de perfil (nombre/username) sin backend todavía: se actualiza la
  // misma sesión local que loadCurrentUser() lee, dejando la estructura lista
  // para reemplazar por una llamada real (ej. PATCH /api/users/me) más adelante.
  const updateStoredUser = (patch) => {
    const current = readStoredUser();
    if (!current) return null;
    const updated = { ...current, ...patch };
    localStorage.setItem(USER_KEY, JSON.stringify(updated));
    setUser(updated);
    return updated;
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    loadCurrentUser,
    updateStoredUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }
  return context;
}
