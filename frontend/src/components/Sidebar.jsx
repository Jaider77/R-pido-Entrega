import { Link } from "react-router-dom";
import useAuthStore from "../stores/authStore";

export default function Sidebar() {
  const token = useAuthStore((s) => s.token);

  if (!token) {
    return null;
  }

  return (
    <aside
      className="sidebar"
      style={{
        width: "250px",
        backgroundColor: "white",
        padding: "1rem",
        borderRadius: "var(--border-radius)",
      }}
    >
      <nav>
        <ul style={{ listStyle: "none" }}>
          <li>
            <Link
              to="/"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              Inicio
            </Link>
          </li>
          <li>
            <Link
              to="/dashboard"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              Panel de Control
            </Link>
          </li>
          <li>
            <Link
              to="/rutas"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              Rutas
            </Link>
          </li>
          <li>
            <Link
              to="/notificaciones"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              Notificaciones
            </Link>
          </li>
          <li>
            <Link
              to="/profile"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              Perfil
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
