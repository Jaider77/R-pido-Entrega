import { Link } from "react-router-dom";
import useAuthStore from "../stores/authStore";

export default function Sidebar() {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);

  if (!token) {
    return null;
  }

  return (
    <aside
      className="sidebar"
      style={{
        width: "250px",
        backgroundColor: "rgba(246, 244, 244, 0.53)",
        padding: "1rem",
        borderRadius: "var(--border-radius)",
      }}
    >
      <nav>
        <div style={{ marginBottom: "0.75rem" }}>
          <details>
            <summary style={{ cursor: "pointer", fontWeight: 600 }}>Navegación</summary>
            <ul style={{ listStyle: "none", paddingLeft: 0, marginTop: "0.5rem" }}>
              <li>
                <Link to="/" style={{ textDecoration: "none", color: "var(--primary)" }}>
                  Inicio
                </Link>
              </li>
              <li>
                <Link to={user?.role === "admin" ? "/admin" : "/dashboard"} style={{ textDecoration: "none", color: "var(--primary)" }}>
                  Panel de Control
                </Link>
              </li>
              <li>
                <Link to="/rutas" style={{ textDecoration: "none", color: "var(--primary)" }}>
                  Rutas
                </Link>
              </li>
              <li>
                <Link to="/notificaciones" style={{ textDecoration: "none", color: "var(--primary)" }}>
                  Notificaciones
                </Link>
              </li>
            </ul>
          </details>
        </div>

        <div>
          <details>
            <summary style={{ cursor: "pointer", fontWeight: 600 }}>Cuenta</summary>
            <ul style={{ listStyle: "none", paddingLeft: 0, marginTop: "0.5rem" }}>
              <li>
                <Link to="/profile" style={{ textDecoration: "none", color: "var(--primary)" }}>
                  Perfil
                </Link>
              </li>
              {user?.role === "repartidor" && (
                <li>
                  <Link to="/repartidor-profile" style={{ textDecoration: "none", color: "var(--primary)" }}>
                    Perfil repartidor
                  </Link>
                </li>
              )}
              {user?.role === "admin" && (
                <li>
                  <Link to="/admin" style={{ textDecoration: "none", color: "var(--primary)" }}>
                    Administrador
                  </Link>
                </li>
              )}
            </ul>
          </details>
        </div>
      </nav>
    </aside>
  );
}
