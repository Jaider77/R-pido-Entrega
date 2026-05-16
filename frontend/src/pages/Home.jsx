import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="card">
      <h1>Bienvenidos a Rápido-Entrega</h1>
      <p>
        Plataforma logística de microservicios para gestión de repartidores y
        rutas
      </p>
      <Link to="/login" className="btn-primary">
        Iniciar Sesión
      </Link>
    </div>
  );
}
