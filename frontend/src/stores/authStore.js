import { create } from "zustand";
import { authService } from "../services";

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem("token") || null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authService.login({ email, password });
      localStorage.setItem("token", data.access_token);
      set({ token: data.access_token, user: data.user });
    } catch (error) {
      set({ error: error.response?.data?.detail || "Login failed" });
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (email, password, fullName) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authService.register({
        email,
        password,
        full_name: fullName,
      });
      set({ user: data });
    } catch (error) {
      set({ error: error.response?.data?.detail || "Registration failed" });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    set({ user: null, token: null });
  },

  getMe: async () => {
    try {
      const { data } = await authService.getMe();
      set({ user: data });
    } catch (error) {
      set({ user: null, token: null });
    }
  },
}));

export default useAuthStore;
