"""
Admin routes for the authentication service.
"""


from app.database import get_db
from app.models import User
from app.routes import get_current_user
from app.schemas import UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter()


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="User role: admin, user, repartidor")


def is_admin_email(email: str) -> bool:
    return email.lower().endswith("@admin.com")


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin" and not is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/admin/users", response_model=list[UserResponse])
async def list_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_admin_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/admin/users/{user_id}", response_model=UserResponse)
async def update_admin_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.role is not None:
        if user_update.role not in {"admin", "user", "repartidor"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )
        user.role = user_update.role

    if user_update.full_name is not None:
        user.full_name = user_update.full_name

    if getattr(user_update, "is_active", None) is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)
    return user


@router.post("/admin/users/{user_id}/roles", response_model=UserResponse)
async def change_admin_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    if role_update.role not in {"admin", "user", "repartidor"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user
