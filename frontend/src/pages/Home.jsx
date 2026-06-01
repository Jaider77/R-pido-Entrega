import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home-container">
      <div className="card main-card">
        <h1>Bienvenidos a Rápido-Entrega</h1>
        <p>
          Plataforma logística de microservicios para gestión de repartidores,
          rutas y notificaciones.
        </p>
        <Link to="/login" className="btn-primary">
          Iniciar Sesión
        </Link>
      </div>

      {/* Sección de cartas motivacionales */}
      <div className="cards-section">
        <div className="cardp">
          <h2>🚀 Oportunidad de empleo</h2>
          <p>
            Únete como repartidor y sé parte de una red que conecta pedidos con
            entregas rápidas y seguras.
          </p>
        </div>

        <div className="cardp">
          <h2>📦 Solución a retrasos</h2>
          <p>
            Tu pedido de Shein, Temu o AliExpress llega más rápido gracias a
            nuestra gestión inteligente de rutas.
          </p>
        </div>

        <div className="cardp">
          <h2>🤝 Colabora con nosotros</h2>
          <p>
            Si eres emprendedor o empresa, podemos trabajar juntos para mejorar
            la experiencia de entrega en tu comunidad.
          </p>
        </div>

        <div className="cardp">
          <h2>🌍 Impacto social</h2>
          <p>
            Nuestra misión es dar empleo a personas y reducir los tiempos de
            espera en las entregas.
          </p>
        </div>

        <div className="cardp">
          <h2>💰 Generación de ingresos</h2>
          <p>
            Con R‑Entrega puedes convertir tu tiempo libre en ingresos extra
            trabajando como repartidor independiente.
          </p>
        </div>

        <div className="cardp">
          <h2>📲 Comunícate con nosotros</h2>
          <p>
            Encuéntranos en nuestras plataformas y redes sociales bajo el nombre
            <strong> R‑Entrega</strong>. ¡Estamos siempre disponibles para ti!
          </p>
        </div>
      </div>
    </div>
  );
}
