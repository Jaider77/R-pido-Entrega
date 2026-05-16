import { Navigate } from "react-router-dom";
import useAuthStore from "../stores/authStore";

export default function ProtectedRoute({ children }) {
  const token = useAuthStore((state) => state.token);
  const isLoading = useAuthStore((state) => state.isLoading);

  if (isLoading) {
    return <div style={{ padding: "2rem" }}>Cargando sesión...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
