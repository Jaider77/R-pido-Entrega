"""
SQLAlchemy models for notifications service
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class NotificationType(str, Enum):
    """Notification type enum"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status enum"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class Notification(Base):
    """Notification model"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    notification_type = Column(
        SQLEnum(NotificationType),
        default=NotificationType.EMAIL,
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recipient = Column(String(255), nullable=False)  # email, phone, or user_id
    sender_id = Column(Integer, nullable=True, index=True)
    parent_id = Column(Integer, ForeignKey("notifications.id"), nullable=True, index=True)
    thread_id = Column(Integer, nullable=True, index=True)
    status = Column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.PENDING,
        nullable=False,
    )
    is_read = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"


class NotificationTemplate(Base):
    """Notification template model"""

    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<NotificationTemplate(id={self.id}, name={self.name})>"


class NotificationLog(Base):
    """Notification log model for audit trail"""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # sent, failed, delivered, read
    details = Column(Text, nullable=True)
    timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<NotificationLog(id={self.id}, action={self.action})>"
