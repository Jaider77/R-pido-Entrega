"""Database migration helper for the rutas service."""

from app.database import Base, engine, ensure_rutas_schema


def main() -> None:
    """Run schema migrations before the app starts."""
    Base.metadata.create_all(bind=engine)
    ensure_rutas_schema()
    print("Rutas service database schema is up to date.")


if __name__ == "__main__":
    main()
