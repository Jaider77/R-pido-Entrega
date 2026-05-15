import useAuthStore from "../stores/authStore";

export default function Dashboard() {
  const { user } = useAuthStore();

  return (
    <div className="card">
      <h2>Dashboard</h2>
      {user ? (
        <>
          <p>Welcome, {user.full_name}!</p>
          <p>Email: {user.email}</p>
          <p>Role: {user.role}</p>
        </>
      ) : (
        <p>Please log in to access the dashboard</p>
      )}
    </div>
  );
}
