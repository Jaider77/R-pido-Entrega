"""
Pydantic schemas for authentication service
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: str
    role: str = Field(default="user", description="User role: admin, user, repartidor")


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request schema"""

    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""

    old_password: str
    new_password: str = Field(min_length=8)


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str
    new_password: str = Field(min_length=8)


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
