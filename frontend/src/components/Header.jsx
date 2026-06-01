import { NavLink, useNavigate } from "react-router-dom";
import useAuthStore from "../stores/authStore";
import Avatar from "./Avatar";
import logo from "../image/logo.png";

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
          maxWidth: "1000px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >

        
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <img src={logo} alt="Logo" style={{ height: "85px", width: "auto" }} />
          <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: "bold", letterSpacing: "0.5px", fontFamily: "'Poppins', 'Segoe UI', sans-serif" }}>Rápido-Entrega</h1>
        </div>
        <nav style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          {token && user ? (
            <>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
                <Avatar size={32} />
                <span style={{ color: "white" }}> {user.full_name}</span>
              </span>
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
          ) : null}
        </nav>
      </div>
    </header>
  );
}
