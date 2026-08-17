import { api } from "@shared/lib/api";

// El backend (POST /api/login) solo devuelve { email, name } -- API_CONTRACT.md §4.1,
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

    localStorage.setItem("token", res.data.token);
    localStorage.setItem("user", JSON.stringify(user));

    return user;
  };

  // POST /api/register no existe en el backend (API_CONTRACT.md §4.2) -- no hay
  // llamada real a la API. Persiste localmente los datos que el usuario ya escribió
  // en el formulario para que el Feed pueda mostrar su identidad real, sin inventar
  // ningún dato ni fingir un token de sesión que no fue emitido por el backend.
  const registerLocally = ({ name, username, email }) => {
    const user = { name, username, email };
    localStorage.setItem("user", JSON.stringify(user));
    return user;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  const getStoredUser = () => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  };

  // Edición de perfil (nombre/username) sin backend todavía: se actualiza la
  // misma sesión local que getStoredUser() lee, dejando la estructura lista
  // para reemplazar por una llamada real (ej. PATCH /api/users/me) más adelante.
  const updateStoredUser = (patch) => {
    const current = getStoredUser();
    if (!current) return null;
    const updated = { ...current, ...patch };
    localStorage.setItem("user", JSON.stringify(updated));
    return updated;
  };

  return { login, registerLocally, logout, getStoredUser, updateStoredUser };
}