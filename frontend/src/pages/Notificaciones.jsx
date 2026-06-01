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

const initialReply = {
  notificationId: null,
  senderId: null,
  title: "",
  message: "",
};

const notificationTypeLabels = {
  email: "Correo",
  sms: "SMS",
  push: "Push",
  in_app: "In-App",
};

const notificationStatusLabels = {
  pending: "Pendiente",
  sent: "Enviado",
  delivered: "Entregado",
  failed: "Fallida",
  read: "Leído",
  unread: "No leído",
};

const translateNotificationStatus = (status) =>
  notificationStatusLabels[status] || status || "-";

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
  const [replyState, setReplyState] = useState(initialReply);
  const [replySending, setReplySending] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, filterRead]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!loading && user) {
        fetchNotifications();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [loading, user, filterRead]);

  useEffect(() => {
    const results = notifications.filter((notification) => {
      const matchesType =
        filterType === "all" || notification.notification_type === filterType;
      const searchValue = searchTerm.toLowerCase();
      const title = (notification.title || "").toLowerCase();
      const message = (notification.message || "").toLowerCase();
      const matchesSearch =
        title.includes(searchValue) || message.includes(searchValue);
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

  const respondNotification = async (
    notificationId,
    senderId,
    originalTitle,
  ) => {
    if (!senderId) {
      toast.error("No se encontró el remitente para esta notificación.");
      return;
    }
    setReplyState({
      notificationId,
      senderId,
      title: originalTitle ? `Re: ${originalTitle}` : "",
      message: "",
    });
  };

  const cancelReply = () => {
    setReplyState(initialReply);
  };

  const handleReplyChange = (event) => {
    const { name, value } = event.target;
    setReplyState((prev) => ({ ...prev, [name]: value }));
  };

  const handleReplySubmit = async (event) => {
    event.preventDefault();
    if (!replyState.senderId) {
      toast.error("No hay destinatario definido para la respuesta.");
      return;
    }
    if (!replyState.title || !replyState.message) {
      toast.error("Debes completar el título y el mensaje de respuesta.");
      return;
    }

    setReplySending(true);
    try {
      await notificacionesService.createNotification({
        user_id: replyState.senderId,
        recipient: String(replyState.senderId),
        parent_id: replyState.notificationId,
        title: replyState.title,
        message: replyState.message,
        notification_type: "in_app",
      });
      await notificacionesService.updateNotification(replyState.notificationId, {
        is_read: true,
      });
      toast.success("Respuesta enviada correctamente.");
      setReplyState(initialReply);
      fetchNotifications();
    } catch (error) {
      toast.error("No se pudo enviar la respuesta.");
    } finally {
      setReplySending(false);
    }
  };

  return (
    <div>
      <div className="card">
        <h1>Notificaciones</h1>
        <p>
          Envía mensajes y revisa el historial de notificaciones de tu usuario.
        </p>
      </div>

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
              placeholder="Destinatario (ID de usuario o correo electrónico)"
              value={form.recipient}
              onChange={handleChange}
              required
            />
            <select
              name="notification_type"
              value={form.notification_type}
              onChange={handleChange}
            >
              <option value="email">Correo</option>
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
              <option value="email">Correo</option>
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
                  <>
                    <tr
                      key={notification.id}
                    style={{ borderTop: "1px solid #e5e7eb" }}
                  >
                    <td style={{ padding: "0.75rem" }}>{notification.title}</td>
                    <td style={{ padding: "0.75rem" }}>
                      {notificationTypeLabels[notification.notification_type] ||
                        notification.notification_type}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {translateNotificationStatus(notification.status)}
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
                      {!notification.is_read ? (
                        notification.sender_id ? (
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={() =>
                              respondNotification(
                                notification.id,
                                notification.sender_id,
                                notification.title,
                              )
                            }
                          >
                            Responder
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={() => markAsRead(notification.id)}
                          >
                            Marcar leída
                          </button>
                        )
                      ) : (
                        <span>Respondido</span>
                      )}
                    </td>
                  </tr>
                  {replyState.notificationId === notification.id && (
                    <tr>
                      <td colSpan="6" style={{ padding: "0.75rem", background: "#f8fafc" }}>
                        <div style={{ display: "grid", gap: "1rem" }}>
                          <strong>Responder mensaje</strong>
                          <form onSubmit={handleReplySubmit}>
                            <input
                              type="text"
                              name="title"
                              placeholder="Título de respuesta"
                              value={replyState.title}
                              onChange={handleReplyChange}
                              required
                            />
                            <textarea
                              name="message"
                              placeholder="Escribe tu respuesta aquí"
                              value={replyState.message}
                              onChange={handleReplyChange}
                              rows={4}
                              required
                            />
                            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                              <button
                                type="submit"
                                className="btn-primary"
                                disabled={replySending}
                              >
                                {replySending ? "Enviando respuesta..." : "Enviar respuesta"}
                              </button>
                              <button
                                type="button"
                                className="btn-secondary"
                                onClick={cancelReply}
                                disabled={replySending}
                              >
                                Cancelar
                              </button>
                            </div>
                          </form>
                        </div>
                      </td>
                    </tr>
                  )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
