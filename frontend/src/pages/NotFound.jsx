export default function NotFound() {
  return (
    <div className="card">
      <h1>404 - Página no encontrada</h1>
      <p>La página que buscas no existe.</p>
      <button
        className="btn-primary"
        onClick={() => (window.location.href = "/")}
      >
        Volver al inicio
      </button>
    </div>
  );
}
