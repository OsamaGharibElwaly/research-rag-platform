import { create } from "zustand";
import type { AuthState, User, Tokens } from "@/types";

interface AuthStore extends AuthState {
  isHydrated: boolean;
  setUser: (user: User | null) => void;
  setTokens: (tokens: Tokens | null) => void;
  login: (user: User, tokens: Tokens) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  hydrateFromStorage: () => boolean;
  setHydrated: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  isHydrated: false,

  setUser: (user) => set({ user }),
  setTokens: (tokens) => set({ tokens }),

  login: (user, tokens) => {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    set({ user, tokens, isAuthenticated: true, isHydrated: true });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isHydrated: true,
    });
  },

  setLoading: (isLoading) => set({ isLoading }),

  hydrateFromStorage: () => {
    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    if (accessToken && refreshToken) {
      set({
        tokens: {
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: "bearer",
          expires_in: 1800,
        },
        isAuthenticated: true,
      });
      return true;
    }

    set({ isAuthenticated: false });
    return false;
  },

  setHydrated: () => set({ isHydrated: true }),
}));
