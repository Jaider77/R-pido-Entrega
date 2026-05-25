import apiClient from "./api";
import adminService from "./adminService";

const authService = {
  register: (data) => apiClient.post("/auth/register", data),
  login: (data) => apiClient.post("/auth/login", data),
  getMe: () => apiClient.get("/auth/me"),
  upgradeToRepartidor: () => apiClient.post("/auth/upgrade-to-repartidor"),
  logout: async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        await apiClient.post("/auth/logout", { refresh_token: refreshToken });
      }
    } catch (err) {
      // ignore errors on logout
    } finally {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
    }
  },
};

const rutasService = {
  createRepartidor: (data) => apiClient.post("/rutas/repartidores", data),
  getMyRepartidorProfile: () => apiClient.get("/rutas/repartidores/me"),
  getRepartidor: (id) => apiClient.get(`/rutas/repartidores/${id}`),
  listRepartidores: (params) =>
    apiClient.get("/rutas/repartidores", { params }),
  updateRepartidor: (id, data) =>
    apiClient.put(`/rutas/repartidores/${id}`, data),
  createRuta: (data) => apiClient.post("/rutas/rutas", data),
  getRuta: (id) => apiClient.get(`/rutas/rutas/${id}`),
  listRutas: (params) => apiClient.get("/rutas/rutas", { params }),
  updateRuta: (id, data) => apiClient.put(`/rutas/rutas/${id}`, data),
  updateLocation: (rutaId, data) =>
    apiClient.post(`/rutas/rutas/${rutaId}/location`, data),
  getLocationHistory: (rutaId, params) =>
    apiClient.get(`/rutas/rutas/${rutaId}/locations`, { params }),
  getRouteStatusHistory: (rutaId) =>
    apiClient.get(`/rutas/rutas/${rutaId}/status-history`),
  getRepartidorStats: (id) => apiClient.get(`/rutas/stats/repartidor/${id}`),
};

const notificacionesService = {
  createNotification: (data) => apiClient.post("/notificaciones/", data),
  getNotification: (id) => apiClient.get(`/notificaciones/${id}`),
  getUserNotifications: (userId, params) =>
    apiClient.get(`/notificaciones/user/${userId}`, { params }),
  updateNotification: (id, data) =>
    apiClient.put(`/notificaciones/${id}`, data),
  deleteNotification: (id) => apiClient.delete(`/notificaciones/${id}`),
  createTemplate: (data) => apiClient.post("/notificaciones/templates/", data),
  getTemplate: (id) => apiClient.get(`/notificaciones/templates/${id}`),
  listTemplates: (params) =>
    apiClient.get("/notificaciones/templates/", { params }),
  getUserStats: (userId, params) =>
    apiClient.get(`/notificaciones/stats/user/${userId}`, { params }),
  sendBulk: (data) => apiClient.post("/notificaciones/send/bulk", data),
};

const service3 = {
  createItem: (data, params) =>
    apiClient.post("/service3/items", data, { params }),
  getItem: (id) => apiClient.get(`/service3/items/${id}`),
  listItems: (params) => apiClient.get("/service3/items", { params }),
  updateItem: (id, data) => apiClient.put(`/service3/items/${id}`, data),
  deleteItem: (id) => apiClient.delete(`/service3/items/${id}`),
  createActivity: (data, params) =>
    apiClient.post("/service3/activities", data, { params }),
  getActivities: (itemId, params) =>
    apiClient.get(`/service3/activities/${itemId}`, { params }),
  getOwnerStats: (ownerId) => apiClient.get(`/service3/stats/owner/${ownerId}`),
};

export {
  authService,
  rutasService,
  notificacionesService,
  service3,
  adminService,
};
