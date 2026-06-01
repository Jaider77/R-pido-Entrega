import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import useAuthStore from "../stores/authStore";
import { adminService } from "../services";

export default function Admin() {
  const user = useAuthStore((state) => state.user);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  const [repartidores, setRepartidores] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [historial, setHistorial] = useState([]);

  const statusLabels = {
    pending: "Pendiente",
    assigned: "Asignada",
    in_transit: "En tránsito",
    delivered: "Entregado",
    cancelled: "Cancelada",
    failed: "Fallida",
    created: "Creado",
    received: "Recibido",
    completed: "Completado",
  };

  const overviewLabels = {
    total_rutas: "Total rutas",
    pending: "Pendientes",
    assigned: "Asignadas",
    "in transit": "En tránsito",
    in_transit: "En tránsito",
    delivered: "Entregadas",
    total_repartidores: "Total repartidores",
    active_repartidores: "Repartidores activos",
    total_users: "Total usuarios",
    active_users: "Usuarios activos",
    total_pedidos: "Total pedidos",
  };

  const translateStatus = (status) => statusLabels[status] || status || "-";
  const translateOverviewLabel = (label) => {
    const normalized = label.replaceAll("_", " ").toLowerCase();
    return overviewLabels[normalized] || label.replaceAll("_", " ");
  };

  useEffect(() => {
    if (!user) return;
    if (user.role !== "admin") {
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const [overviewResp, usersResp, repsResp, pedidosResp, historyResp] =
          await Promise.all([
            adminService.getOverview(),
            adminService.listUsers({ limit: 10 }),
            adminService.listRepartidores({ limit: 10 }),
            adminService.listPedidos({ limit: 10 }),
            adminService.getDailyHistory(),
          ]);

        setOverview(overviewResp.data);
        setUsers(usersResp.data);
        setRepartidores(repsResp.data);
        setPedidos(pedidosResp.data);
        setHistorial(historyResp.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "No se pudo cargar la información del administrador.",
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (!user) {
    return <div style={{ padding: "2rem" }}>Cargando perfil...</div>;
  }

  if (user.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="card" style={{ padding: "1.5rem" }}>
      <h2>Panel de Administrador</h2>
      {loading && <p>Cargando datos...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {overview && (
        <details open className="admin-panel-section">
          <summary>Resumen</summary>
          <table className="admin-table">
            <thead>
              <tr>
                <th>Campo</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(overview).map(([label, value]) => (
                <tr key={label}>
                  <td>{translateOverviewLabel(label)}</td>
                  <td>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}

      <details open className="admin-panel-section">
        <summary>Usuarios recientes ({users.length})</summary>
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Correo electrónico</th>
              <th>Nombre</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {users.map((userItem) => (
              <tr key={userItem.id}>
                <td>{userItem.id}</td>
                <td>{userItem.email}</td>
                <td>{userItem.full_name}</td>
                <td>{userItem.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>

      <details open className="admin-panel-section">
        <summary>Repartidores ({repartidores.length})</summary>
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Teléfono</th>
              <th>Vehículo</th>
              <th>Activo</th>
            </tr>
          </thead>
          <tbody>
            {repartidores.map((rep) => (
              <tr key={rep.id}>
                <td>{rep.id}</td>
                <td>{rep.phone}</td>
                <td>{rep.vehicle_type}</td>
                <td>{rep.is_active ? "Sí" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>

      <details open className="admin-panel-section">
        <summary>Pedidos recientes ({pedidos.length})</summary>
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Estado</th>
              <th>Repartidor</th>
              <th>Creado por</th>
            </tr>
          </thead>
          <tbody>
            {pedidos.map((pedido) => (
              <tr key={pedido.id}>
                <td>{pedido.id}</td>
                <td>{translateStatus(pedido.status)}</td>
                <td>{pedido.repartidor_id || "Sin asignar"}</td>
                <td>{pedido.created_by_user_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>

      <details open className="admin-panel-section">
        <summary>Historial diario ({historial.length})</summary>
        {historial.length ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Estado</th>
                <th>Completado el</th>
              </tr>
            </thead>
            <tbody>
              {historial.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{translateStatus(item.status)}</td>
                  <td>{new Date(item.completed_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No hay entregas completadas en el día seleccionado.</p>
        )}
      </details>
    </div>
  );
}
