export default function Header() {
  return (
    <header
      className="header"
      style={{
        backgroundColor: "var(--primary)",
        color: "white",
        padding: "1rem",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>📦 Rápido-Entrega</h1>
        <nav>
          <a
            href="/"
            style={{
              color: "white",
              marginRight: "1rem",
              textDecoration: "none",
            }}
          >
            Inicio
          </a>
          <a
            href="/dashboard"
            style={{ color: "white", textDecoration: "none" }}
          >
            Panel de Control
          </a>
        </nav>
      </div>
    </header>
  );
}
