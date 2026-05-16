import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "/api";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle responses and attempt refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const resp = await axios.post(`${API_URL}/auth/refresh-token`, {
            refresh_token: refreshToken,
          });

          const newAccess = resp.data.access_token;
          const newRefresh = resp.data.refresh_token;
          if (newAccess) {
            localStorage.setItem("token", newAccess);
            if (newRefresh) localStorage.setItem("refresh_token", newRefresh);
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return apiClient(originalRequest);
          }
        } catch (err) {
          // refresh failed
        }
      }

      // fallback: clear and redirect to login
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default apiClient;
