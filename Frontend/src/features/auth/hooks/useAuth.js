import { api } from "@shared/lib/api";

export function useAuth() {

  const login = async (data) => {
    const res = await api.post("/login", data);

    localStorage.setItem("token", res.data.token);

    return res.data.user;
  };

  return { login };
}