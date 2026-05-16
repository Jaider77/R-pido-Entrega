import { useEffect, useState } from "react";
import { rutasService } from "../services";
import toast from "react-hot-toast";

const initialForm = {
  repartidor_id: "",
  delivery_id: "",
  origin_latitude: "",
  origin_longitude: "",
  destination_latitude: "",
  destination_longitude: "",
  notes: "",
};

export default function Rutas() {
  const [routes, setRoutes] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchRoutes();
  }, []);

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      const { data } = await rutasService.listRutas({ limit: 50 });
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
        repartidor_id: Number(form.repartidor_id),
        delivery_id: Number(form.delivery_id),
        origin_latitude: Number(form.origin_latitude),
        origin_longitude: Number(form.origin_longitude),
        destination_latitude: Number(form.destination_latitude),
        destination_longitude: Number(form.destination_longitude),
        notes: form.notes,
      };
      await rutasService.createRuta(payload);
      toast.success("Ruta creada correctamente");
      setForm(initialForm);
      fetchRoutes();
    } catch (error) {
      toast.error("Error al crear la ruta. Verifique los datos.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h1>Rutas</h1>
        <p>Administra entregas y visualiza las rutas activas.</p>
      </div>

      <div className="card">
        <h2>Crear nueva ruta</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gap: "1rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            <input
              type="number"
              name="repartidor_id"
              placeholder="ID de repartidor"
              value={form.repartidor_id}
              onChange={handleChange}
              required
            />
            <input
              type="number"
              name="delivery_id"
              placeholder="ID de entrega"
              value={form.delivery_id}
              onChange={handleChange}
              required
            />
            <input
              type="number"
              name="origin_latitude"
              placeholder="Latitud origen"
              value={form.origin_latitude}
              onChange={handleChange}
              step="0.000001"
              required
            />
            <input
              type="number"
              name="origin_longitude"
              placeholder="Longitud origen"
              value={form.origin_longitude}
              onChange={handleChange}
              step="0.000001"
              required
            />
            <input
              type="number"
              name="destination_latitude"
              placeholder="Latitud destino"
              value={form.destination_latitude}
              onChange={handleChange}
              step="0.000001"
              required
            />
            <input
              type="number"
              name="destination_longitude"
              placeholder="Longitud destino"
              value={form.destination_longitude}
              onChange={handleChange}
              step="0.000001"
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
      </div>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>Listado de rutas</h2>
          <button className="btn-secondary" onClick={fetchRoutes} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {routes.length === 0 ? (
          <p>No hay rutas registradas todavía.</p>
        ) : (
          <div style={{ overflowX: "auto", marginTop: "1rem" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>ID</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Repartidor</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Entrega</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Status</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Origen</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Destino</th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>Creada</th>
                </tr>
              </thead>
              <tbody>
                {routes.map((ruta) => (
                  <tr key={ruta.id} style={{ borderTop: "1px solid #e5e7eb" }}>
                    <td style={{ padding: "0.75rem" }}>{ruta.id}</td>
                    <td style={{ padding: "0.75rem" }}>{ruta.repartidor_id}</td>
                    <td style={{ padding: "0.75rem" }}>{ruta.delivery_id}</td>
                    <td style={{ padding: "0.75rem" }}>{ruta.status}</td>
                    <td style={{ padding: "0.75rem" }}>
                      {ruta.origin_latitude}, {ruta.origin_longitude}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {ruta.destination_latitude}, {ruta.destination_longitude}
                    </td>
                    <td style={{ padding: "0.75rem" }}>{new Date(ruta.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
