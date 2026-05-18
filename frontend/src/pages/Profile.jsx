import useAuthStore from "../stores/authStore";

export default function Profile() {
  const { user } = useAuthStore();

  return (
    <div className="card">
      <h1>Perfil</h1>
      {user ? (
        <>
          <p>
            <strong>Nombre:</strong> {user.full_name}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          <p>
            <strong>Rol:</strong> {user.role}
          </p>
        </>
      ) : (
        <p>Inicie sesión para ver su perfil.</p>
      )}
    </div>
  );
}
