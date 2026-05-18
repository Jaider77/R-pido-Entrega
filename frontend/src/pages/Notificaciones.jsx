import { useEffect, useState } from "react";
import { notificacionesService } from "../services";
import useAuthStore from "../stores/authStore";
import toast from "react-hot-toast";

const initialForm = {
  title: "",
  message: "",
  recipient: "",
  notification_type: "email",
};

export default function Notificaciones() {
  const user = useAuthStore((s) => s.user);
  const [notifications, setNotifications] = useState([]);
  const [filteredNotifications, setFilteredNotifications] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [filterType, setFilterType] = useState("all");
  const [filterRead, setFilterRead] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, filterRead]);

  useEffect(() => {
    const results = notifications.filter((notification) => {
      const matchesType =
        filterType === "all" || notification.notification_type === filterType;
      const searchValue = searchTerm.toLowerCase();
      const matchesSearch =
        notification.title.toLowerCase().includes(searchValue) ||
        notification.message.toLowerCase().includes(searchValue);
      return matchesType && matchesSearch;
    });

    setFilteredNotifications(results);
  }, [notifications, filterType, searchTerm]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const params = { limit: 50 };
      if (filterRead !== "all") {
        params.is_read = filterRead === "read";
      }
      let { data } = await notificacionesService.getUserNotifications(
        user.id,
        params,
      );
      if ((!data || data.length === 0) && user.email) {
        const fallbackParams = { ...params, recipient: user.email };
        const fallbackResponse =
          await notificacionesService.getUserNotifications(
            user.id,
            fallbackParams,
          );
        data = fallbackResponse.data;
      }
      setNotifications(data || []);
    } catch (error) {
      toast.error("No se pudieron cargar las notificaciones.");
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
    if (!user) {
      toast.error("Necesitas iniciar sesión para enviar notificaciones.");
      return;
    }

    setSending(true);
    try {
      const targetUserId = Number(form.recipient);
      const userIdToSend =
        !Number.isNaN(targetUserId) && targetUserId > 0
          ? targetUserId
          : user.id;

      await notificacionesService.createNotification({
        user_id: userIdToSend,
        title: form.title,
        message: form.message,
        recipient: form.recipient,
        notification_type: form.notification_type,
      });
      toast.success("Notificación enviada correctamente");
      setForm(initialForm);
      fetchNotifications();
    } catch (error) {
      toast.error("Error al enviar la notificación.");
    } finally {
      setSending(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificacionesService.updateNotification(notificationId, {
        is_read: true,
      });
      toast.success("Notificación marcada como leída");
      fetchNotifications();
    } catch (error) {
      toast.error("No se pudo actualizar la notificación.");
    }
  };

  const respondNotification = async (notificationId) => {
    try {
      await notificacionesService.updateNotification(notificationId, {
        is_read: true,
      });
      toast.success("Notificación respondida correctamente.");
      fetchNotifications();
    } catch (error) {
      toast.error("No se pudo responder la notificación.");
    }
  };

  const canSendNotifications = user?.role !== "repartidor";

  return (
    <div>
      <div className="card">
        <h1>Notificaciones</h1>
        <p>
          Envía mensajes y revisa el historial de notificaciones de tu usuario.
        </p>
      </div>

      {canSendNotifications ? (
        <div className="card">
          <h2>Enviar notificación</h2>
          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gap: "1rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              }}
            >
              <input
                type="text"
                name="title"
                placeholder="Título"
                value={form.title}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="recipient"
                placeholder="Destinatario (ID de usuario o email)"
                value={form.recipient}
                onChange={handleChange}
                required
              />
              <select
                name="notification_type"
                value={form.notification_type}
                onChange={handleChange}
              >
                <option value="email">Email</option>
                <option value="sms">SMS</option>
                <option value="push">Push</option>
                <option value="in_app">In-App</option>
              </select>
            </div>
            <textarea
              name="message"
              placeholder="Mensaje"
              value={form.message}
              onChange={handleChange}
              rows={4}
              required
            />
            <button type="submit" className="btn-primary" disabled={sending}>
              {sending ? "Enviando..." : "Enviar notificación"}
            </button>
          </form>
        </div>
      ) : (
        <div className="card">
          <h2>Responder notificaciones</h2>
          <p>
            Como repartidor solo puedes responder las notificaciones que te
            lleguen. Usa el botón "Responder" cuando recibas un mensaje.
          </p>
        </div>
      )}

      <div className="card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <h2>Historial de notificaciones</h2>
            <p>
              {notifications.length} notificaciones totales,{" "}
              {notifications.filter((item) => !item.is_read).length} sin leer.
            </p>
          </div>
          <button
            className="btn-secondary"
            onClick={fetchNotifications}
            disabled={loading}
          >
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        <div className="stats-grid" style={{ marginTop: "1rem" }}>
          <div>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              Filtrar por tipo
            </label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">Todos</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push</option>
              <option value="in_app">In-App</option>
            </select>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              Filtrar por lectura
            </label>
            <select
              value={filterRead}
              onChange={(e) => setFilterRead(e.target.value)}
            >
              <option value="all">Todos</option>
              <option value="read">Leídos</option>
              <option value="unread">No leídos</option>
            </select>
          </div>
          <div style={{ minWidth: "220px" }}>
            <label style={{ display: "block", marginBottom: "0.5rem" }}>
              Buscar
            </label>
            <input
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar título o mensaje"
            />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setFilterType("all");
                setFilterRead("all");
                setSearchTerm("");
              }}
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        {filteredNotifications.length === 0 ? (
          <p style={{ marginTop: "1rem" }}>
            No se encontraron notificaciones para tu filtro.
          </p>
        ) : (
          <div style={{ overflowX: "auto", marginTop: "1rem" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Título
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Tipo
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Estado
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Leído
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Enviado
                  </th>
                  <th style={{ textAlign: "left", padding: "0.75rem" }}>
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredNotifications.map((notification) => (
                  <tr
                    key={notification.id}
                    style={{ borderTop: "1px solid #e5e7eb" }}
                  >
                    <td style={{ padding: "0.75rem" }}>{notification.title}</td>
                    <td style={{ padding: "0.75rem" }}>
                      {notification.notification_type}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {notification.status}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {notification.is_read ? "Sí" : "No"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {notification.sent_at
                        ? new Date(notification.sent_at).toLocaleString()
                        : "-"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {user?.role === "repartidor" ? (
                        !notification.is_read ? (
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={() => respondNotification(notification.id)}
                          >
                            Responder
                          </button>
                        ) : (
                          <span>Respondido</span>
                        )
                      ) : (
                        !notification.is_read && (
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={() => markAsRead(notification.id)}
                          >
                            Marcar leída
                          </button>
                        )
                      )}
                    </td>
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
