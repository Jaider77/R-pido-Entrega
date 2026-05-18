import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../stores/authStore";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("user");
  const { register, login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await register(email, password, fullName, role);
    if (success) {
      const user = await login(email, password);
      if (user) {
        const redirectPath =
          user.role === "repartidor" ? "/repartidor-profile" : "/dashboard";
        navigate(redirectPath, { replace: true });
      } else {
        navigate("/login", { replace: true });
      }
    }
  };

  return (
    <div className="card" style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h2>Crear cuenta</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nombre completo"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={8}
          required
        />
        <select value={role} onChange={(e) => setRole(e.target.value)} required>
          <option value="user">Usuario</option>
          <option value="repartidor">Repartidor</option>
        </select>
        <small>La contraseña debe tener al menos 8 caracteres.</small>
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? "Registrando..." : "Crear cuenta"}
        </button>
      </form>
      <p style={{ marginTop: "1rem" }}>
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </div>
  );
}
