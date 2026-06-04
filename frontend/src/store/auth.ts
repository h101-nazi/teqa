"use client";

import { create } from "zustand";

interface AuthState {
  token: string | null;
  user: { id: string; email: string; full_name: string } | null;
  setAuth: (token: string, user: { id: string; email: string; full_name: string }) => void;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  setAuth: (token, user) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("teqa_token", token);
      localStorage.setItem("teqa_user", JSON.stringify(user));
    }
    set({ token, user });
  },
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("teqa_token");
      localStorage.removeItem("teqa_user");
    }
    set({ token: null, user: null });
  },
  hydrate: () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("teqa_token");
      const userStr = localStorage.getItem("teqa_user");
      if (token && userStr) {
        set({ token, user: JSON.parse(userStr) });
      }
    }
  },
}));
