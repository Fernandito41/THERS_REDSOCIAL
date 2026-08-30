import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@shared/lib/api";

const AuthContext = createContext(undefined);

const TOKEN_KEY = "token";
const USER_KEY = "user";

// El backend ya devuelve `username` real (ADR-002, API_CONTRACT.md §4). Este
// fallback solo cubre sesiones guardadas en localStorage antes de ese cambio,
// que no tienen la columna todavía -- no es la fuente principal.
function withUsername(user) {
  return {
    ...user,
    username: user.username || user.email.split("@")[0],
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fuente de verdad de la identidad: GET /api/users/me (API_CONTRACT.md
  // §4.2, ADR-002). Un token inválido/expirado (401) o un usuario que ya no
  // existe (404) limpian la sesión local vía logout().
  const loadCurrentUser = async () => {
    setIsLoading(true);
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
      setUser(null);
      setIsLoading(false);
      return null;
    }

    try {
      const res = await api.get("/users/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const currentUser = withUsername(res.data.user);
      localStorage.setItem(USER_KEY, JSON.stringify(currentUser));
      setUser(currentUser);
      return currentUser;
    } catch {
      logout();
      return null;
    } finally {
      setIsLoading(false);
    }
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

  // Edición de perfil (name/username/phone/country_code/birth_date):
  // persistida por el backend (ADR-003, API_CONTRACT.md §4.2). La respuesta
  // de PATCH /api/users/me reemplaza `user` por completo -- misma fuente de
  // verdad que login()/loadCurrentUser(), nunca un merge parcial local.
  const updateProfile = async (patch) => {
    const token = localStorage.getItem(TOKEN_KEY);
    const res = await api.patch("/users/me", patch, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const updatedUser = withUsername(res.data.user);

    localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
    setUser(updatedUser);

    return updatedUser;
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    loadCurrentUser,
    updateProfile,
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
