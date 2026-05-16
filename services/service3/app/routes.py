"""
Service3 endpoints
"""

from typing import List, Optional

import httpx
from app.config import settings
from app.database import get_db
from app.models import Activity, Item
from app.schemas import ActivityCreate, ActivityResponse, ItemCreate, ItemResponse, ItemUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

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
            return response.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )


# ============================================
# ITEM ENDPOINTS
# ============================================


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create a new item"""
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    owner_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """List items"""
    query = db.query(Item)

    if owner_id:
        query = query.filter(Item.owner_id == owner_id)

    return query.offset(skip).limit(limit).all()


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Update item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Delete item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    db.delete(db_item)
    db.commit()


# ============================================
# ACTIVITY ENDPOINTS
# ============================================


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create activity log entry"""
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.get("/activities/{item_id}", response_model=List[ActivityResponse])
async def get_item_activities(
    item_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get activities for an item"""
    activities = (
        db.query(Activity)
        .filter(Activity.item_id == item_id)
        .order_by(Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return activities


# ============================================
# STATS ENDPOINTS
# ============================================


@router.get("/stats/owner/{owner_id}")
async def get_owner_stats(
    owner_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get statistics for an owner"""
    total_items = db.query(Item).filter(Item.owner_id == owner_id).count()
    active_items = db.query(Item).filter(Item.owner_id == owner_id, Item.status == "active").count()

    return {
        "owner_id": owner_id,
        "total_items": total_items,
        "active_items": active_items,
        "inactive_items": total_items - active_items,
    }
