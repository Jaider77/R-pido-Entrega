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


def is_postgres():
    """Return True when the current engine is PostgreSQL."""
    return engine.dialect.name == "postgresql"


def get_column_data_type(table_name: str, column_name: str) -> str:
    """Return the SQL data type for a table column in PostgreSQL."""
    if not is_postgres():
        return ""
    sql = """
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = :table_name AND column_name = :column_name
    """
    with engine.begin() as conn:
        return (
            conn.execute(
                text(sql),
                {"table_name": table_name, "column_name": column_name},
            ).scalar()
            or ""
        )


def is_timestamp_without_timezone(table_name: str, column_name: str) -> bool:
    """Return True if a PostgreSQL column is timestamp without time zone."""
    return get_column_data_type(table_name, column_name) == "timestamp without time zone"


def is_integer_column(table_name: str, column_name: str) -> bool:
    """Return True if a PostgreSQL column is an integer type."""
    return get_column_data_type(table_name, column_name) == "integer"


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
    if "origin_address" not in columns:
        missing_columns.append("ALTER TABLE rutas ADD COLUMN origin_address TEXT")
    if "destination_address" not in columns:
        missing_columns.append("ALTER TABLE rutas ADD COLUMN destination_address TEXT")

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

        # Make origin/destination coordinates nullable if currently NOT NULL
        for col in (
            "origin_latitude",
            "origin_longitude",
            "destination_latitude",
            "destination_longitude",
        ):
            if col in columns and not columns[col].get("nullable", True):
                if engine.dialect.name == "postgresql":
                    logger.info("Making %s nullable in rutas table.", col)
                    conn.execute(text(f"ALTER TABLE rutas ALTER COLUMN {col} DROP NOT NULL"))
                elif engine.dialect.name == "sqlite":
                    logger.info(
                        "SQLite does not support DROP NOT NULL via ALTER TABLE; migration skipped for %s.",
                        col,
                    )

        if is_timestamp_without_timezone("rutas", "created_at"):
            logger.info("Altering rutas.created_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE rutas ALTER COLUMN created_at TYPE timestamptz USING created_at AT TIME ZONE 'UTC'"
                )
            )
        if is_timestamp_without_timezone("rutas", "started_at"):
            logger.info("Altering rutas.started_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE rutas ALTER COLUMN started_at TYPE timestamptz USING started_at AT TIME ZONE 'UTC'"
                )
            )
        if is_timestamp_without_timezone("rutas", "completed_at"):
            logger.info("Altering rutas.completed_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE rutas ALTER COLUMN completed_at TYPE timestamptz USING completed_at AT TIME ZONE 'UTC'"
                )
            )


def ensure_repartidores_schema():
    """Ensure repartidores schema is compatible with the current models."""
    inspector = inspect(engine)
    if "repartidores" not in inspector.get_table_names():
        logger.info("repartidores table not found, skipping schema ensure.")
        return

    columns = {col["name"]: col for col in inspector.get_columns("repartidores")}
    alter_sql = []

    if "latitude" in columns and not columns["latitude"].get("nullable", True):
        if engine.dialect.name == "postgresql":
            alter_sql.append("ALTER TABLE repartidores ALTER COLUMN latitude DROP NOT NULL")
        elif engine.dialect.name == "sqlite":
            logger.info(
                "SQLite does not support DROP NOT NULL via ALTER TABLE; repartidores.latitude migration skipped."
            )
    if "longitude" in columns and not columns["longitude"].get("nullable", True):
        if engine.dialect.name == "postgresql":
            alter_sql.append("ALTER TABLE repartidores ALTER COLUMN longitude DROP NOT NULL")
        elif engine.dialect.name == "sqlite":
            logger.info(
                "SQLite does not support DROP NOT NULL via ALTER TABLE; repartidores.longitude migration skipped."
            )

    with engine.begin() as conn:
        for sql in alter_sql:
            logger.info("Applying schema change to repartidores: %s", sql)
            conn.execute(text(sql))

        if is_timestamp_without_timezone("repartidores", "created_at"):
            logger.info("Altering repartidores.created_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE repartidores ALTER COLUMN created_at TYPE timestamptz USING created_at AT TIME ZONE 'UTC'"
                )
            )
        if is_timestamp_without_timezone("repartidores", "updated_at"):
            logger.info("Altering repartidores.updated_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE repartidores ALTER COLUMN updated_at TYPE timestamptz USING updated_at AT TIME ZONE 'UTC'"
                )
            )
        if is_integer_column("repartidores", "is_active"):
            logger.info("Altering repartidores.is_active to boolean.")
            conn.execute(
                text(
                    "ALTER TABLE repartidores ALTER COLUMN is_active TYPE boolean USING is_active::boolean"
                )
            )


def ensure_location_history_schema():
    """Ensure location_history schema is compatible with the current models."""
    inspector = inspect(engine)
    if "location_history" not in inspector.get_table_names():
        logger.info("location_history table not found, skipping schema ensure.")
        return

    with engine.begin() as conn:
        if is_timestamp_without_timezone("location_history", "timestamp"):
            logger.info("Altering location_history.timestamp to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE location_history ALTER COLUMN timestamp TYPE timestamptz USING timestamp AT TIME ZONE 'UTC'"
                )
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

        if is_timestamp_without_timezone("ruta_status_history", "changed_at"):
            logger.info("Altering ruta_status_history.changed_at to timestamptz.")
            conn.execute(
                text(
                    "ALTER TABLE ruta_status_history ALTER COLUMN changed_at TYPE timestamptz USING changed_at AT TIME ZONE 'UTC'"
                )
            )


async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    try:
        ensure_rutas_schema()
        ensure_repartidores_schema()
        ensure_location_history_schema()
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
