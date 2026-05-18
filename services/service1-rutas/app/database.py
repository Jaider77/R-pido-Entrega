"""
Database configuration and session management
"""

import logging

from app.config import settings
from app.models import Base
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# Database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def ensure_rutas_schema():
    """Ensure routes schema is compatible with the current models."""
    inspector = inspect(engine)
    if "rutas" not in inspector.get_table_names():
        logger.info("Rutas table not found, skipping schema ensure.")
        return

    columns = {col["name"]: col for col in inspector.get_columns("rutas")}
    missing_columns = []

    if "created_by_user_id" not in columns:
        missing_columns.append("ALTER TABLE rutas ADD COLUMN created_by_user_id INTEGER")
    if "last_changed_by_name" not in columns:
        missing_columns.append("ALTER TABLE rutas ADD COLUMN last_changed_by_name VARCHAR(150)")
    if "last_changed_by_plate" not in columns:
        missing_columns.append("ALTER TABLE rutas ADD COLUMN last_changed_by_plate VARCHAR(50)")

    with engine.begin() as conn:
        for sql in missing_columns:
            logger.info("Applying schema change: %s", sql)
            conn.execute(text(sql))

        if "repartidor_id" in columns:
            repartidor_column = columns["repartidor_id"]
            if not repartidor_column.get("nullable", True):
                if engine.dialect.name == "postgresql":
                    logger.info("Making repartidor_id nullable in rutas table.")
                    conn.execute(text("ALTER TABLE rutas ALTER COLUMN repartidor_id DROP NOT NULL"))
                elif engine.dialect.name == "sqlite":
                    logger.info(
                        "SQLite does not support DROP NOT NULL via ALTER TABLE; migration skipped for repartidor_id."
                    )


def ensure_ruta_status_history_schema():
    """Ensure ruta_status_history schema is compatible with the current models."""
    inspector = inspect(engine)
    if "ruta_status_history" not in inspector.get_table_names():
        logger.info("ruta_status_history table not found, skipping schema ensure.")
        return

    columns = {col["name"]: col for col in inspector.get_columns("ruta_status_history")}
    missing_columns = []

    if "changed_by_repartidor_id" not in columns:
        missing_columns.append(
            "ALTER TABLE ruta_status_history ADD COLUMN changed_by_repartidor_id INTEGER"
        )
    if "changed_by_name" not in columns:
        missing_columns.append(
            "ALTER TABLE ruta_status_history ADD COLUMN changed_by_name VARCHAR(150)"
        )
    if "changed_by_plate" not in columns:
        missing_columns.append(
            "ALTER TABLE ruta_status_history ADD COLUMN changed_by_plate VARCHAR(50)"
        )

    with engine.begin() as conn:
        for sql in missing_columns:
            logger.info("Applying schema change to ruta_status_history: %s", sql)
            conn.execute(text(sql))


async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    try:
        ensure_rutas_schema()
        ensure_ruta_status_history_schema()
    except Exception as exc:
        logger.warning("Could not migrate existing schema: %s", exc)
    logger.info("Database tables initialized")


def get_db():
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
