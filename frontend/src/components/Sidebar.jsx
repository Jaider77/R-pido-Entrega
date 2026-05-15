export default function Sidebar() {
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
            <a
              href="/"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              🏠 Inicio
            </a>
          </li>
          <li>
            <a
              href="/dashboard"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              📊 Dashboard
            </a>
          </li>
          <li>
            <a
              href="/rutas"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              🗺️ Rutas
            </a>
          </li>
          <li>
            <a
              href="/notificaciones"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              🔔 Notificaciones
            </a>
          </li>
          <li>
            <a
              href="/profile"
              style={{ textDecoration: "none", color: "var(--primary)" }}
            >
              👤 Perfil
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
