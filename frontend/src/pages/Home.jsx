export default function Home() {
  return (
    <div className="card">
      <h1>Bienvenidos a Rápido-Entrega</h1>
      <p>
        Plataforma logística de microservicios para gestión de repartidores y
        rutas
      </p>
      <button
        className="btn-primary"
        onClick={() => (window.location.href = "/login")}
      >
        Iniciar Sesión
      </button>
    </div>
  );
}
