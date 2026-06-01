"""
Pydantic schemas for notifications service
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    """Notification type"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class NotificationBase(BaseModel):
    """Base notification schema"""

    title: str
    message: str
    recipient: str
    notification_type: NotificationType = NotificationType.EMAIL


class NotificationCreate(NotificationBase):
    """Notification creation schema"""

    user_id: Optional[int] = None
    parent_id: Optional[int] = None
    is_read: bool = False


class NotificationUpdate(BaseModel):
    """Notification update schema"""

    is_read: Optional[bool] = None
    status: Optional[NotificationStatus] = None


class NotificationResponse(NotificationBase):
    """Notification response schema"""

    id: int
    user_id: int
    sender_id: Optional[int]
    status: NotificationStatus
    parent_id: Optional[int]
    thread_id: Optional[int]
    is_read: bool
    error_message: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationTemplateBase(BaseModel):
    """Base notification template schema"""

    name: str
    title_template: str
    message_template: str
    notification_type: NotificationType


class NotificationTemplateCreate(NotificationTemplateBase):
    """Notification template creation schema"""

    pass


class NotificationTemplateResponse(NotificationTemplateBase):
    """Notification template response schema"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendNotificationRequest(BaseModel):
    """Request to send notification"""

    user_id: int
    template_name: str
    recipient: str
    context: Optional[dict] = Field(default_factory=dict)
