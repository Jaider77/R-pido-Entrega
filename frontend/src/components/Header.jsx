import { NavLink, useNavigate } from "react-router-dom";
import useAuthStore from "../stores/authStore";
import Avatar from "./Avatar";

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header
      className="header"
      style={{
        backgroundColor: "var(--primary)",
        color: "white",
        padding: "1rem",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>📦 Rápido-Entrega</h1>
        <nav>
          <NavLink
            to="/"
            style={({ isActive }) => ({
              color: "white",
              marginRight: "1rem",
              textDecoration: "none",
              opacity: isActive ? 0.85 : 1,
            })}
          >
            Inicio
          </NavLink>
          {token && user ? (
            <NavLink to="/profile" style={{ textDecoration: "none" }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", marginRight: "1rem", opacity: 0.95 }}>
                <Avatar size={32} />
                <span style={{ color: "white" }}>Hola, {user.full_name}</span>
              </span>
            </NavLink>
          ) : null}
          {token ? (
            <>
              <NavLink
                to="/dashboard"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  marginRight: "1rem",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Panel de Control
              </NavLink>
              <NavLink
                to="/rutas"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  marginRight: "1rem",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Rutas
              </NavLink>
              <NavLink
                to="/notificaciones"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  marginRight: "1rem",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Notificaciones
              </NavLink>
              <NavLink
                to="/profile"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  marginRight: "1rem",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Perfil
              </NavLink>
              <button
                onClick={handleLogout}
                style={{
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.2)",
                  color: "white",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  marginRight: "1rem",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Iniciar sesión
              </NavLink>
              <NavLink
                to="/register"
                style={({ isActive }) => ({
                  color: "white",
                  textDecoration: "none",
                  opacity: isActive ? 0.85 : 1,
                })}
              >
                Registro
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
