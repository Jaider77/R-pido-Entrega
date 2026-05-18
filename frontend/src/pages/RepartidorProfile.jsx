import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { rutasService } from "../services";

export default function RepartidorProfile() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    phone: "",
    vehicle_type: "motorcycle",
    license_plate: "",
  });

  useEffect(() => {
    if (!user) return;
    if (user.role !== "repartidor") {
      navigate("/dashboard", { replace: true });
      return;
    }
    fetchProfile();
  }, [user, navigate]);

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
      toast.error("No se pudo crear el perfil de repartidor.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card">
      <h1>Perfil de repartidor</h1>
      <p>
        Configura tu perfil de repartidor para comenzar a trabajar con rutas.
      </p>

      {loading ? (
        <p>Cargando...</p>
      ) : profile ? (
        <div>
          <p>
            <strong>Usuario:</strong> {user?.full_name}
          </p>
          <p>
            <strong>Email:</strong> {user?.email}
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
          <button
            className="btn-primary"
            onClick={() => navigate("/dashboard", { replace: true })}
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
