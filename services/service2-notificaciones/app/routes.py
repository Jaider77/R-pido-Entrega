"""
Notification endpoints
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from app.config import settings
from app.database import get_db
from app.models import Notification, NotificationLog, NotificationStatus, NotificationTemplate
from app.schemas import (
    NotificationCreate,
    NotificationResponse,
    NotificationTemplateCreate,
    NotificationTemplateResponse,
    NotificationUpdate,
    SendNotificationRequest,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


async def verify_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token with authentication service"""
    token = credentials.credentials
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/api/auth/verify-token",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            payload = response.json().get("payload")
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            payload["token"] = token
            return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )


def render_template(template: str, context: dict) -> str:
    """Render basic notification template using context values"""
    try:
        return template.format(**context)
    except Exception:
        return template


async def resolve_recipient_user_id(
    recipient: str, default_user_id: Optional[int], auth_token: Optional[str]
) -> Optional[int]:
    """Resolve an internal user ID from recipient information."""
    if not recipient:
        return default_user_id

    if recipient.isdigit():
        return int(recipient)

    if "@" in recipient and auth_token:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/auth/users/by-email",
                    params={"email": recipient},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )
                if response.status_code == 200:
                    return response.json().get("id")
        except Exception:
            return default_user_id

    return default_user_id


# ============================================
# NOTIFICATION ENDPOINTS
# ============================================


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create and send a notification"""
    notification_data = notification.model_dump()
    notification_data["user_id"] = await resolve_recipient_user_id(
        notification_data.get("recipient"),
        notification_data.get("user_id"),
        auth.get("token"),
    )
    if notification_data.get("user_id") is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resolve recipient user id",
        )
    db_notification = Notification(**notification_data)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Prototype behavior: mark notification as sent and store sent time
    db_notification.status = NotificationStatus.SENT
    db_notification.sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_notification)

    # Create audit log for the notification
    notification_log = NotificationLog(
        notification_id=db_notification.id,
        action="sent",
        details=f"Notification sent to {db_notification.recipient}",
    )
    db.add(notification_log)
    db.commit()

    logger.info(
        "Notification %s queued as sent for recipient %s",
        db_notification.id,
        db_notification.recipient,
    )

    return db_notification


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get notification by ID"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    is_read: Optional[bool] = None,
    recipient: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get notifications for a user"""
    query = db.query(Notification)
    if recipient:
        query = query.filter(Notification.recipient == recipient)
    else:
        query = query.filter(Notification.user_id == user_id)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Update notification (mark as read, update status)"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    for field, value in notification_update.model_dump(exclude_unset=True).items():
        setattr(db_notification, field, value)

    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Delete notification"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    db.delete(db_notification)
    db.commit()


# ============================================
# TEMPLATE ENDPOINTS
# ============================================


@router.post(
    "/templates/", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create notification template"""
    existing = (
        db.query(NotificationTemplate).filter(NotificationTemplate.name == template.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists",
        )

    db_template = NotificationTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def get_notification_template(
    template_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get notification template by ID"""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return template


@router.get("/templates/", response_model=List[NotificationTemplateResponse])
async def list_notification_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """List all notification templates"""
    return (
        db.query(NotificationTemplate)
        .order_by(NotificationTemplate.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================
# BULK ENDPOINTS
# ============================================


@router.post("/send/bulk", status_code=status.HTTP_202_ACCEPTED)
async def send_bulk_notifications(
    notifications: List[SendNotificationRequest],
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Send bulk notifications"""
    created_notifications = []

    for notif_request in notifications:
        # Get template
        template = (
            db.query(NotificationTemplate)
            .filter(NotificationTemplate.name == notif_request.template_name)
            .first()
        )
        if not template:
            continue

        # Create notification using the chosen template and context
        notification = Notification(
            user_id=notif_request.user_id,
            notification_type=template.notification_type,
            title=render_template(template.title_template, notif_request.context),
            message=render_template(template.message_template, notif_request.context),
            recipient=notif_request.recipient,
            status=NotificationStatus.PENDING,
        )
        db.add(notification)
        created_notifications.append(notification)

    db.commit()

    # Create audit logs for queued notifications
    for notification in created_notifications:
        log = NotificationLog(
            notification_id=notification.id,
            action="queued",
            details=f"Bulk notification queued for {notification.recipient}",
        )
        db.add(log)
    db.commit()

    return {
        "sent": len(created_notifications),
        "message": "Bulk notifications queued for sending",
    }


# ============================================
# STATS ENDPOINTS
# ============================================


@router.get("/stats/user/{user_id}")
async def get_user_notification_stats(
    user_id: int,
    recipient: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get notification statistics for a user"""
    query = db.query(Notification)
    if recipient:
        query = query.filter(Notification.recipient == recipient)
    else:
        query = query.filter(Notification.user_id == user_id)

    total = query.count()
    unread = query.filter(Notification.is_read.is_(False)).count()
    sent = query.filter(Notification.status == NotificationStatus.SENT).count()
    failed = query.filter(Notification.status == NotificationStatus.FAILED).count()

    return {
        "user_id": user_id,
        "total": total,
        "unread": unread,
        "sent": sent,
        "failed": failed,
        "unread_percentage": (unread / total * 100) if total > 0 else 0,
    }
