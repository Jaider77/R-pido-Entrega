export default function NotFound() {
  return (
    <div className="card">
      <h1>404 - Page Not Found</h1>
      <p>La página que buscas no existe.</p>
      <button
        className="btn-primary"
        onClick={() => (window.location.href = "/")}
      >
        Volver al Inicio
      </button>
    </div>
  );
}
