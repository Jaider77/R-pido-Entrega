import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { rutasService, notificacionesService } from "../services";

export default function Dashboard() {
  const { user } = useAuthStore();
  const [routeStats, setRouteStats] = useState(null);
  const [notificationStats, setNotificationStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.role === "admin") {
      navigate("/admin", { replace: true });
      return;
    }

    if (user) {
      fetchStats();
    }
  }, [user, navigate]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      let repartidorId = user.id;
      if (user.role === "repartidor") {
        try {
          const profileResponse = await rutasService.getMyRepartidorProfile();
          repartidorId = profileResponse.data.id;
        } catch (error) {
          if (error.response?.status === 404) {
            toast.error(
              "Debe crear su perfil de repartidor para ver estadísticas de rutas.",
            );
            repartidorId = null;
          } else {
            throw error;
          }
        }
      }

      const [routesResponse, notifsResponse] = await Promise.all([
        repartidorId
          ? rutasService.getRepartidorStats(repartidorId)
          : Promise.resolve({
              data: {
                total_deliveries: 0,
                delivered: 0,
                in_transit: 0,
                pending: 0,
                success_rate: 0,
              },
            }),
        notificacionesService.getUserStats(user.id),
      ]);
      let notificationData = notifsResponse.data;
      if ((!notificationData || notificationData.total === 0) && user.email) {
        const fallbackResponse = await notificacionesService.getUserStats(
          user.id,
          {
            recipient: user.email,
          },
        );
        notificationData = fallbackResponse.data;
      }
      setRouteStats(routesResponse.data);
      setNotificationStats(notificationData);
    } catch (error) {
      console.error(error);
      toast.error("No se pudieron cargar las estadísticas.");
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (path) => navigate(path);

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div>
            <h1>Panel de Control</h1>
            <p>Resumen de tu actividad en Rápido-Entrega.</p>
          </div>
          <div className="section-actions">
            <button
              className="btn-secondary"
              onClick={() => handleNavigate("/rutas")}
            >
              Ver rutas
            </button>
            <button
              className="btn-secondary"
              onClick={() => handleNavigate("/notificaciones")}
            >
              Ver notificaciones
            </button>
          </div>
        </div>

        {!user ? (
          <p>Inicie sesión para acceder al panel de control.</p>
        ) : (
          <div>
            <div className="stats-grid">
              <div className="stat-card">
                <strong>Usuario</strong>
                <span>{user.full_name}</span>
                <p style={{ marginTop: "0.5rem" }}>{user.email}</p>
                <p style={{ color: "#4b5563" }}>Rol: {user.role}</p>
              </div>
              <div className="stat-card">
                <strong>Rutas activas</strong>
                <span>{routeStats?.total_deliveries ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>Total de rutas asignadas</p>
              </div>
              <div className="stat-card">
                <strong>Notificaciones</strong>
                <span>{notificationStats?.total ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>
                  Mensajes enviados o recibidos
                </p>
              </div>
            </div>

            <div className="stats-grid" style={{ marginTop: "1rem" }}>
              <div className="stat-card">
                <strong>Entregadas</strong>
                <span>{routeStats?.delivered ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>Rutas completadas</p>
              </div>
              <div className="stat-card">
                <strong>En tránsito</strong>
                <span>{routeStats?.in_transit ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>Rutas en curso</p>
              </div>
              <div className="stat-card">
                <strong>Sin leer</strong>
                <span>{notificationStats?.unread ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>Notificaciones pendientes</p>
              </div>
            </div>

            <div className="stats-grid" style={{ marginTop: "1rem" }}>
              <div className="stat-card">
                <strong>Ratio de éxito</strong>
                <span>
                  {routeStats ? `${routeStats.success_rate.toFixed(1)}%` : "-"}
                </span>
                <p style={{ color: "#4b5563" }}>
                  Porcentaje de entregas completadas
                </p>
              </div>
              <div className="stat-card">
                <strong>En cola</strong>
                <span>{routeStats ? routeStats.pending : "-"}</span>
                <p style={{ color: "#4b5563" }}>Rutas pendientes</p>
              </div>
              <div className="stat-card">
                <strong>Fallidas</strong>
                <span>{notificationStats?.failed ?? "-"}</span>
                <p style={{ color: "#4b5563" }}>Notificaciones con error</p>
              </div>
            </div>

            <div style={{ marginTop: "1.5rem" }}>
              <button
                className="btn-primary"
                onClick={fetchStats}
                disabled={loading}
              >
                {loading ? "Actualizando..." : "Actualizar estadísticas"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
