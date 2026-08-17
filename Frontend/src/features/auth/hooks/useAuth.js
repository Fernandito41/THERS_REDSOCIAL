import { api } from "@shared/lib/api";

const TOKEN_KEY = "token";
const USER_KEY = "user";

// El backend (POST /api/login) solo devuelve { id, email, name } -- API_CONTRACT.md §4.1,
// sin username. Se deriva de la parte local del email como valor real (no inventado)
// hasta que exista un campo username ratificado en DATABASE_ARCHITECTURE.md.
function withUsername(user) {
  return {
    ...user,
    username: user.username || user.email.split("@")[0],
  };
}

export function useAuth() {

  const login = async (data) => {
    const res = await api.post("/login", data);
    const user = withUsername(res.data.user);

    localStorage.setItem(TOKEN_KEY, res.data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return user;
  };

  const register = async (data) => {
    const res = await api.post("/register", data);

    return res.data.user;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const getStoredUser = () => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  };

  // Edición de perfil (nombre/username) sin backend todavía: se actualiza la
  // misma sesión local que getStoredUser() lee, dejando la estructura lista
  // para reemplazar por una llamada real (ej. PATCH /api/users/me) más adelante.
  const updateStoredUser = (patch) => {
    const current = getStoredUser();
    if (!current) return null;
    const updated = { ...current, ...patch };
    localStorage.setItem(USER_KEY, JSON.stringify(updated));
    return updated;
  };

  return { login, register, logout, getStoredUser, updateStoredUser };
}
