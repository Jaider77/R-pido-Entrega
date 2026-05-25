import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { rutasService } from "../services";

const activeStatuses = ["pending", "assigned", "in_transit"];
const statusLabels = {
  pending: "Pendiente",
  assigned: "Asignada",
  in_transit: "En tránsito",
};
const statusColors = {
  pending: "#6b7280",
  assigned: "#2563eb",
  in_transit: "#f59e0b",
};

export default function RepartidorProfile() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [routeLoading, setRouteLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeRoutes, setActiveRoutes] = useState([]);
  const [form, setForm] = useState({
    phone: "",
    vehicle_type: "motorcycle",
    license_plate: "",
  });

  useEffect(() => {
    if (!user) return;
    if (user.role !== "repartidor") {
      return;
    }
    fetchProfile();
  }, [user, navigate]);

  useEffect(() => {
    if (profile?.id) {
      fetchActiveRoutes();
    }
  }, [profile]);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const { data } = await rutasService.getMyRepartidorProfile();
      setProfile(data);
    } catch (error) {
      if (error.response?.status !== 404) {
        toast.error("No se pudo cargar el perfil de repartidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchActiveRoutes = async () => {
    setRouteLoading(true);
    try {
      const { data } = await rutasService.listRutas({
        repartidor_id: profile.id,
        limit: 50,
      });
      const active = (data || []).filter((ruta) =>
        activeStatuses.includes(ruta.status),
      );
      setActiveRoutes(active);
    } catch (error) {
      toast.error("No se pudieron cargar las rutas activas.");
    } finally {
      setRouteLoading(false);
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
      const { data } = await rutasService.createRepartidor(form);
      setProfile(data);
      toast.success("Perfil de repartidor creado correctamente.");
      navigate("/dashboard", { replace: true });
    } catch (error) {
      const detail = error.response?.data?.detail || error.message;
      toast.error(`No se pudo crear el perfil de repartidor. ${detail}`);
    } finally {
      setSaving(false);
    }
  };

  if (user?.role !== "repartidor") {
    return (
      <div className="card">
        <h1>Perfil de repartidor</h1>
        <p>
          Tu cuenta no es repartidor todavía. Ve a tu perfil y convierte tu
          cuenta en repartidor para crear el perfil de repartidor.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <h1>Perfil de repartidor</h1>
      <p>
        Configura tu perfil de repartidor y revisa solo las rutas activas
        asignadas a ti.
      </p>

      {loading ? (
        <p>Cargando...</p>
      ) : profile ? (
        <div>
          <p>
            <strong>Usuario:</strong> {user?.full_name}
          </p>
          <p>
            <strong>Correo electrónico:</strong> {user?.email}
          </p>
          <p>
            <strong>Teléfono:</strong> {profile.phone}
          </p>
          <p>
            <strong>Vehículo:</strong> {profile.vehicle_type}
          </p>
          <p>
            <strong>Placa:</strong> {profile.license_plate ?? "No registrada"}
          </p>

          <div className="card" style={{ marginTop: "1.5rem" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <h2>Rutas activas</h2>
                <p>
                  Solo se muestran las rutas en estado pendiente, asignada o en
                  tránsito.
                </p>
              </div>
              <button
                className="btn-secondary"
                onClick={fetchActiveRoutes}
                disabled={routeLoading}
              >
                {routeLoading ? "Actualizando..." : "Actualizar rutas"}
              </button>
            </div>

            {activeRoutes.length === 0 ? (
              <p style={{ marginTop: "1rem" }}>
                No tienes rutas activas en este momento.
              </p>
            ) : (
              <div style={{ overflowX: "auto", marginTop: "1rem" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        ID
                      </th>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        Entrega
                      </th>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        Estado
                      </th>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        Origen
                      </th>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        Destino
                      </th>
                      <th style={{ textAlign: "left", padding: "0.75rem" }}>
                        Notas
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeRoutes.map((ruta) => (
                      <tr
                        key={ruta.id}
                        style={{ borderTop: "1px solid #e5e7eb" }}
                      >
                        <td style={{ padding: "0.75rem" }}>{ruta.id}</td>
                        <td style={{ padding: "0.75rem" }}>
                          {ruta.delivery_id}
                        </td>
                        <td style={{ padding: "0.75rem" }}>
                          <span
                            style={{
                              display: "inline-block",
                              backgroundColor:
                                statusColors[ruta.status] || "#6b7280",
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
                          {ruta.origin_latitude}, {ruta.origin_longitude}
                        </td>
                        <td style={{ padding: "0.75rem" }}>
                          {ruta.destination_latitude},{" "}
                          {ruta.destination_longitude}
                        </td>
                        <td style={{ padding: "0.75rem" }}>
                          {ruta.notes || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <button
            className="btn-primary"
            onClick={() => navigate("/dashboard", { replace: true })}
            style={{ marginTop: "1rem" }}
          >
            Ir al panel
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          style={{ maxWidth: "500px", gap: "1rem", display: "grid" }}
        >
          <label>
            Teléfono
            <input
              type="text"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="Teléfono"
              required
            />
          </label>
          <label>
            Tipo de vehículo
            <select
              name="vehicle_type"
              value={form.vehicle_type}
              onChange={handleChange}
              required
            >
              <option value="motorcycle">Motocicleta</option>
              <option value="bike">Bicicleta</option>
              <option value="car">Auto</option>
            </select>
          </label>
          <label>
            Placa
            <input
              type="text"
              name="license_plate"
              value={form.license_plate}
              onChange={handleChange}
              placeholder="Placa"
            />
          </label>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? "Guardando..." : "Crear perfil de repartidor"}
          </button>
        </form>
      )}
    </div>
  );
}
