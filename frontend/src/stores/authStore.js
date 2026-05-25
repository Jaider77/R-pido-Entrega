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
      if (data.refresh_token)
        localStorage.setItem("refresh_token", data.refresh_token);
      set({ token: data.access_token, user: data.user });
      return data.user;
    } catch (error) {
      const detail = error.response?.data?.detail;
      set({
        error: Array.isArray(detail)
          ? detail.map((item) => item.msg).join(". ")
          : detail || "Error de inicio de sesión",
      });
      return null;
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (email, password, fullName, role = "user") => {
    set({ isLoading: true, error: null });
    try {
      await authService.register({
        email,
        password,
        full_name: fullName,
        role,
      });
      return true;
    } catch (error) {
      const detail = error.response?.data?.detail;
      set({
        error: Array.isArray(detail)
          ? detail.map((item) => item.msg).join(". ")
          : detail || "Error al registrar la cuenta",
      });
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    await authService.logout();
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
  // Initialize store from localStorage
  init: async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const { data } = await authService.getMe();
        set({ user: data, token });
      } catch (err) {
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token");
        set({ user: null, token: null });
      }
    }
  },
}));

export default useAuthStore;
