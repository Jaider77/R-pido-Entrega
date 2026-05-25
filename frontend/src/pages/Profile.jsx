import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";

export default function Profile() {
  const { user, upgradeToRepartidor } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpgrade = async () => {
    setLoading(true);
    const updatedUser = await upgradeToRepartidor();
    setLoading(false);
    if (updatedUser) {
      toast.success("Tu cuenta ahora es repartidor.");
      navigate("/repartidor-profile", { replace: true });
    } else {
      toast.error("No se pudo cambiar a repartidor. Intenta nuevamente.");
    }
  };

  return (
    <div className="card">
      <h1>Perfil</h1>
      {user ? (
        <>
          <p>
            <strong>Nombre:</strong> {user.full_name}
          </p>
          <p>
            <strong>Correo electrónico:</strong> {user.email}
          </p>
          <p>
            <strong>Rol:</strong> {user.role}
          </p>
          {user.role !== "repartidor" && (
            <div style={{ marginTop: "1.5rem" }}>
              <p>
                Para crear un perfil de repartidor y acceder a las rutas
                asignadas, convierte tu cuenta en repartidor.
              </p>
              <button
                className="btn-primary"
                onClick={handleUpgrade}
                disabled={loading}
              >
                {loading ? "Actualizando..." : "Convertirme en repartidor"}
              </button>
            </div>
          )}
        </>
      ) : (
        <p>Inicie sesión para ver su perfil.</p>
      )}
    </div>
  );
}
