import { createContext, useContext, useState } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const { data } = await client.post("/auth/login", { email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  };

  const register = async (email, password, full_name) => {
    await client.post("/auth/register", { email, password, full_name });
  };

  const logout = async () => {
    const refresh_token = localStorage.getItem("refresh_token");
    try {
      await client.post("/auth/logout", { refresh_token });
    } catch {
      // ignore — clearing local state regardless
    }
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);