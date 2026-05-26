import { useEffect, useState } from "react";
import { rutasService } from "../services";
import useAuthStore from "../stores/authStore";
import toast from "react-hot-toast";

const initialForm = {
  delivery_id: "",
  origin_address: "",
  destination_address: "",
  notes: "",
};

const statusLabels = {
  pending: "Pendiente",
  assigned: "Asignada",
  in_transit: "Recogido",
  delivered: "Entregado",
  cancelled: "Cancelada",
  failed: "Fallida",
};

const statusColors = {
  pending: "#6b7280",
  assigned: "#2563eb",
  in_transit: "#f59e0b",
  delivered: "#16a34a",
  cancelled: "#dc2626",
  failed: "#ef4444",
};

export default function Rutas() {
  const user = useAuthStore((state) => state.user);
  const [routes, setRoutes] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [repartidorProfile, setRepartidorProfile] = useState(null);

  useEffect(() => {
    if (user?.role === "repartidor") {
      fetchRepartidorProfile();
    } else {
      setRepartidorProfile(null);
    }
  }, [user]);

  useEffect(() => {
    fetchRoutes();
  }, [user, repartidorProfile]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!loading) {
        fetchRoutes();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [loading, user, repartidorProfile]);

  const fetchRepartidorProfile = async () => {
    try {
      const { data } = await rutasService.getMyRepartidorProfile();
      setRepartidorProfile(data);
    } catch (error) {
      if (error.response?.status === 404) {
        setRepartidorProfile(null);
      } else {
        setRepartidorProfile(null);
        toast.error("No se pudo cargar el perfil de repartidor.");
      }
    }
  };

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      if (user?.role === "repartidor" && !repartidorProfile) {
        setRoutes([]);
        return;
      }

      const params = { limit: 50 };
      const { data } = await rutasService.listRutas(params);
      setRoutes(data || []);
    } catch (error) {
      toast.error("No se pudo cargar las rutas.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      const payload = {
        delivery_id: Number(form.delivery_id),
        origin_address: form.origin_address,
        destination_address: form.destination_address,
        notes: form.notes,
      };
      await rutasService.createRuta(payload);
      toast.success("Ruta creada correctamente");
      setForm(initialForm);
      fetchRoutes();
    } catch (error) {
      const apiMessage = error.response?.data?.detail || error.message;
      toast.error(`Error al crear la ruta. ${apiMessage}`);
    } finally {
      setSaving(false);
    }
  };

  const changeRouteStatus = async (rutaId, status) => {
    setActionLoading(true);
    try {
      await rutasService.updateRuta(rutaId, { status });
      toast.success("Estado de la ruta actualizado.");
      fetchRoutes();
    } catch (error) {
      toast.error("No se pudo actualizar el estado de la ruta.");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h1>Rutas</h1>
        <p>Administra entregas y visualiza las rutas activas.</p>
      </div>

      <div className="card">
        <h2>Revisa tu lista de rutas</h2>
        {user?.role === "repartidor" ? (
          repartidorProfile ? (
            <p style={{ color: "#3745df" }}>
              Estas son las rutas abiertas y asignadas que puedes tomar.
            </p>
          ) : (
            <p style={{ color: "#dc2626" }}>
              Debes crear tu perfil de repartidor para ver y tomar rutas
              abiertas.
            </p>
          )
        ) : user?.role === "admin" ? (
          <p style={{ color: "#2563eb" }}>
            Como administrador, no puedes crear rutas desde esta pantalla.
            Revisa solo el listado de rutas disponibles.
          </p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gap: "1rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              }}
            >
              <input
                type="number"
                name="delivery_id"
                placeholder="ID de entrega"
                value={form.delivery_id}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="origin_address"
                placeholder="Origen: Ciudad, Barrio, Calle, #"
                value={form.origin_address}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="destination_address"
                placeholder="Destino: Ciudad, Barrio, Calle, #"
                value={form.destination_address}
                onChange={handleChange}
                required
              />
            </div>
            <textarea
              name="notes"
              placeholder="Notas de la entrega"
              value={form.notes}
              onChange={handleChange}
              rows={3}
            />
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Creando ruta..." : "Crear ruta"}
            </button>
          </form>
        )}
      </div>

      <div className="card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2>Listado de rutas</h2>
        </div>

        {routes.length === 0 ? (
          <p>No hay rutas registradas todavía.</p>
        ) : (
          <div style={{ overflowX: "auto", marginTop: "1rem" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>ID</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Repartidor
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Entrega
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Status
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Origen
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Destino
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Último cambio
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {routes.map((ruta) => {
                  const badgeColor = statusColors[ruta.status] || "#6b7280";
                  const lastChange = ruta.completed_at
                    ? new Date(ruta.completed_at).toLocaleString()
                    : ruta.started_at
                      ? new Date(ruta.started_at).toLocaleString()
                      : "-";

                  return (
                    <tr
                      key={ruta.id}
                      style={{ borderTop: "1px solid #e5e7eb" }}
                    >
                      <td style={{ padding: "0.75rem" }}>{ruta.id}</td>
                      <td style={{ padding: "0.75rem" }}>
                        {ruta.repartidor_id ?? "Sin asignar"}
                      </td>
                      <td style={{ padding: "0.75rem" }}>{ruta.delivery_id}</td>
                      <td style={{ padding: "0.75rem" }}>
                        <span
                          style={{
                            display: "inline-block",
                            backgroundColor: badgeColor,
                            color: "#fff",
                            padding: "0.35rem 0.75rem",
                            borderRadius: "999px",
                            fontSize: "0.85rem",
                          }}
                        >
                          {statusLabels[ruta.status] || ruta.status}
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        {ruta.origin_address ??
                          `${ruta.origin_latitude || ""}, ${
                            ruta.origin_longitude || ""
                          }`}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        {ruta.destination_address ??
                          `${ruta.destination_latitude || ""}, ${
                            ruta.destination_longitude || ""
                          }`}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        {lastChange}
                        {ruta.last_changed_by_name && (
                          <div
                            style={{
                              fontSize: "0.85rem",
                              color: "#374151",
                              marginTop: "0.25rem",
                            }}
                          >
                            Recogido por: {ruta.last_changed_by_name}{" "}
                            {ruta.last_changed_by_plate
                              ? ` / ${ruta.last_changed_by_plate}`
                              : ""}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        {user?.role === "repartidor" ? (
                          ruta.repartidor_id === null &&
                          ruta.status === "pending" ? (
                            <button
                              className="btn-primary"
                              onClick={() =>
                                changeRouteStatus(ruta.id, "assigned")
                              }
                              disabled={actionLoading}
                            >
                              Tomar ruta
                            </button>
                          ) : ruta.repartidor_id === repartidorProfile?.id ? (
                            <div
                              style={{
                                display: "flex",
                                gap: "0.5rem",
                                flexWrap: "wrap",
                              }}
                            >
                              {(ruta.status === "pending" ||
                                ruta.status === "assigned") && (
                                <button
                                  className="btn-secondary"
                                  onClick={() =>
                                    changeRouteStatus(ruta.id, "in_transit")
                                  }
                                  disabled={actionLoading}
                                >
                                  Marcar recogido
                                </button>
                              )}
                              {ruta.status === "in_transit" && (
                                <button
                                  className="btn-primary"
                                  onClick={() =>
                                    changeRouteStatus(ruta.id, "delivered")
                                  }
                                  disabled={actionLoading}
                                >
                                  Marcar entregado
                                </button>
                              )}
                              {ruta.status === "delivered" && (
                                <span>✔ Entregado</span>
                              )}
                            </div>
                          ) : (
                            <span style={{ color: "#4b5563" }}>
                              {ruta.repartidor_id
                                ? "Asignada a otro"
                                : "Sin acción"}
                            </span>
                          )
                        ) : (
                          <span style={{ color: "#4b5563" }}>-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
