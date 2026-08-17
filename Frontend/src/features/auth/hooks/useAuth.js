import { api } from "@shared/lib/api";

const TOKEN_KEY = "token";
const USER_KEY = "user";

export function useAuth() {

  const login = async (data) => {
    const res = await api.post("/login", data);

    localStorage.setItem(TOKEN_KEY, res.data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.data.user));

    return res.data.user;
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

  return { login, register, logout, getStoredUser };
}
