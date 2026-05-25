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
        <section style={{ marginBottom: "1.5rem" }}>
          <h3>Resumen</h3>
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
                  <td>{label.replaceAll("_", " ")}</td>
                  <td>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <section style={{ marginBottom: "1.5rem" }}>
        <h3>Usuarios recientes</h3>
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
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h3>Repartidores</h3>
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
      </section>

      <section>
        <h3>Pedidos recientes</h3>
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
                <td>{pedido.status}</td>
                <td>{pedido.repartidor_id || "Sin asignar"}</td>
                <td>{pedido.created_by_user_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h3>Historial diario</h3>
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
                  <td>{item.status}</td>
                  <td>{new Date(item.completed_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No hay entregas completadas en el día seleccionado.</p>
        )}
      </section>
    </div>
  );
}
