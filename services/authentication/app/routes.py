"""
Authentication routes
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from app.config import settings
from app.database import get_db
from app.models import RefreshToken, User
from app.schemas import (
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.orm import Session

ALLOWED_ROLES = {"admin", "user", "repartidor"}

logger = logging.getLogger(__name__)

router = APIRouter()


def is_admin_email(email: str) -> bool:
    return email.lower().endswith("@admin.com")


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    import jwt

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(db, user_id: int) -> str:
    """Create and persist refresh token"""
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token.token


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    import jwt

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    role = "admin" if is_admin_email(user_data.email) else user_data.role
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT token"""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # Create token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(db, user.id)
    expires_in = settings.jwt_expiration_hours * 3600
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # nosec B106
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.post("/verify-token")
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify JWT token and return decoded payload"""
    payload = verify_token(credentials.credentials)
    return {"valid": True, "payload": payload}


@router.get("/users/by-email", response_model=UserResponse)
async def get_user_by_email(
    email: EmailStr,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a user by email address"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using a refresh token"""
    refresh_token_record = (
        db.query(RefreshToken).filter(RefreshToken.token == token_request.refresh_token).first()
    )

    def is_expired(expiration):
        if expiration is None:
            return True
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        return expiration < datetime.now(timezone.utc)

    if (
        not refresh_token_record
        or refresh_token_record.is_revoked
        or is_expired(refresh_token_record.expires_at)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db.query(User).filter(User.id == refresh_token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    refresh_token_record.is_revoked = True
    db.commit()

    new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    new_refresh_token = create_refresh_token(db, user.id)
    expires_in = settings.jwt_expiration_hours * 3600
    token_type = "bearer"  # nosec B105

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type=token_type,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
):
    """Revoke a refresh token and log out"""
    refresh_token_record = (
        db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    )
    if not refresh_token_record or refresh_token_record.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found or already revoked",
        )

    refresh_token_record.is_revoked = True
    db.commit()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/change-password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password",
        )

    current_user.password_hash = get_password_hash(req.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(req: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset link has been sent"}

    # Generate reset token (simple implementation)
    reset_token = create_access_token(
        data={"sub": str(user.id), "type": "reset"}, expires_delta=timedelta(hours=1)
    )

    # For prototype, log the reset token instead of sending a real email
    logger.info(f"Password reset token for {user.email}: {reset_token}")

    return {"message": "If email exists, reset link has been sent"}


@router.post("/reset-password")
async def reset_password(req: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    try:
        payload = verify_token(req.token)
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password_hash = get_password_hash(req.new_password)
        db.commit()

        return {"message": "Password reset successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "authentication"}
