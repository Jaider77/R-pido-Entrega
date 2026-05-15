export default function NotFound() {
  return (
    <div className="card">
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist</p>
      <button
        className="btn-primary"
        onClick={() => (window.location.href = "/")}
      >
        Go Home
      </button>
    </div>
  );
}
