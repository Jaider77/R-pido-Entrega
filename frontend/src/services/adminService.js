import apiClient from "./api";

const adminService = {
  listUsers: (params) => apiClient.get("/auth/admin/users", { params }),
  getUser: (userId) => apiClient.get(`/auth/admin/users/${userId}`),
  updateUser: (userId, data) =>
    apiClient.patch(`/auth/admin/users/${userId}`, data),
  changeUserRole: (userId, data) =>
    apiClient.post(`/auth/admin/users/${userId}/roles`, data),

  listRepartidores: (params) =>
    apiClient.get("/rutas/admin/repartidores", { params }),
  listPedidos: (params) => apiClient.get("/rutas/admin/pedidos", { params }),
  getOverview: () => apiClient.get("/rutas/admin/seguimiento"),
  getDailyHistory: (params) =>
    apiClient.get("/rutas/admin/historial-diario", { params }),
  downloadPedidoReciboPdf: (pedidoId) =>
    apiClient.get(`/rutas/admin/pedidos/${pedidoId}/recibo/pdf`, {
      responseType: "blob",
    }),
};

export default adminService;
