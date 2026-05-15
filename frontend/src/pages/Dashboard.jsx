import useAuthStore from "../stores/authStore";

export default function Dashboard() {
  const { user } = useAuthStore();

  return (
    <div className="card">
      <h2>Panel de Control</h2>
      {user ? (
        <>
          <p>Bienvenido, {user.full_name}!</p>
          <p>Email: {user.email}</p>
          <p>Rol: {user.role}</p>
        </>
      ) : (
        <p>Inicie sesión para acceder al panel de control</p>
      )}
    </div>
  );
}
