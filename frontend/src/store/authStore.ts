import { create } from "zustand";

export interface User {
  id: number;
  username: string;
  email?: string;
  role: "ADMIN" | "OPERATOR" | "VIEWER";
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  init: () => void;
}

const DEFAULT_ADMIN: User = {
  id: 1,
  username: "admin",
  email: "admin@gridshield.ai",
  role: "ADMIN",
};

export const useAuthStore = create<AuthState>((set) => ({
  user: DEFAULT_ADMIN,
  token: "default-admin-token",
  login: (token, user) => {
    try {
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
    } catch {}
    set({ token, user });
  },
  logout: () => {
    try {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    } catch {}
    set({ token: null, user: null });
  },
  init: () => {
    try {
      const token = localStorage.getItem("token");
      const userStr = localStorage.getItem("user");
      if (token && userStr) {
        set({ token, user: JSON.parse(userStr) });
      } else {
        set({ token: "default-admin-token", user: DEFAULT_ADMIN });
      }
    } catch {
      set({ token: "default-admin-token", user: DEFAULT_ADMIN });
    }
  },
}));
