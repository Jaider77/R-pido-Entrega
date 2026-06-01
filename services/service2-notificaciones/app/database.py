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


def _ensure_sender_id_column():
    inspector = inspect(engine)
    if "notifications" not in inspector.get_table_names():
        return

    columns = [column["name"] for column in inspector.get_columns("notifications")]
    if "sender_id" not in columns:
        logger.info("Adding missing sender_id column to notifications table")
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE notifications ADD COLUMN sender_id INTEGER"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_notifications_sender_id ON notifications (sender_id)"
                )
            )


def _ensure_thread_columns():
    inspector = inspect(engine)
    if "notifications" not in inspector.get_table_names():
        return

    columns = [column["name"] for column in inspector.get_columns("notifications")]
    with engine.begin() as conn:
        if "parent_id" not in columns:
            logger.info("Adding missing parent_id column to notifications table")
            conn.execute(text("ALTER TABLE notifications ADD COLUMN parent_id INTEGER"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_notifications_parent_id ON notifications (parent_id)"
                )
            )
        if "thread_id" not in columns:
            logger.info("Adding missing thread_id column to notifications table")
            conn.execute(text("ALTER TABLE notifications ADD COLUMN thread_id INTEGER"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_notifications_thread_id ON notifications (thread_id)"
                )
            )


async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    _ensure_sender_id_column()
    _ensure_thread_columns()
    logger.info("Database tables initialized")


def get_db():
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
