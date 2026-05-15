"""
Routes and delivery endpoints
"""

from datetime import datetime
from typing import List, Optional

import httpx
from app.config import settings
from app.database import get_db
from app.models import DeliveryStatus, LocationHistory, Repartidor, Ruta
from app.schemas import (
    LocationHistoryResponse,
    LocationUpdate,
    RepartidorCreate,
    RepartidorResponse,
    RepartidorUpdate,
    RutaCreate,
    RutaResponse,
    RutaUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from geopy.distance import geodesic
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
# REPARTIDOR ENDPOINTS
# ============================================


@router.post(
    "/repartidores", response_model=RepartidorResponse, status_code=status.HTTP_201_CREATED
)
async def create_repartidor(
    repartidor: RepartidorCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create a new repartidor"""
    existing = db.query(Repartidor).filter(Repartidor.user_id == repartidor.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repartidor already exists for this user",
        )

    db_repartidor = Repartidor(**repartidor.dict())
    db.add(db_repartidor)
    db.commit()
    db.refresh(db_repartidor)
    return db_repartidor


@router.get("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
async def get_repartidor(
    repartidor_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get repartidor by ID"""
    repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    if not repartidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repartidor not found",
        )
    return repartidor


@router.get("/repartidores", response_model=List[RepartidorResponse])
async def list_repartidores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """List all repartidores"""
    return db.query(Repartidor).offset(skip).limit(limit).all()


@router.put("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
async def update_repartidor(
    repartidor_id: int,
    repartidor_update: RepartidorUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Update repartidor"""
    db_repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    if not db_repartidor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repartidor not found",
        )

    for field, value in repartidor_update.dict(exclude_unset=True).items():
        setattr(db_repartidor, field, value)

    db.commit()
    db.refresh(db_repartidor)
    return db_repartidor


# ============================================
# RUTA ENDPOINTS
# ============================================


@router.post("/rutas", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
async def create_ruta(
    ruta: RutaCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Create a new route/delivery"""
    # Calculate distance
    origin = (ruta.origin_latitude, ruta.origin_longitude)
    destination = (ruta.destination_latitude, ruta.destination_longitude)
    distance_km = geodesic(origin, destination).kilometers

    # Estimate time (assuming average speed of 30 km/h)
    estimated_time = int((distance_km / 30) * 60)

    db_ruta = Ruta(
        **ruta.dict(),
        estimated_distance_km=distance_km,
        estimated_duration_minutes=estimated_time,
        status=DeliveryStatus.PENDING,
    )
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta


@router.get("/rutas/{ruta_id}", response_model=RutaResponse)
async def get_ruta(
    ruta_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get route by ID"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return ruta


@router.get("/rutas", response_model=List[RutaResponse])
async def list_rutas(
    repartidor_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """List routes with optional filters"""
    query = db.query(Ruta)

    if repartidor_id:
        query = query.filter(Ruta.repartidor_id == repartidor_id)

    if status:
        query = query.filter(Ruta.status == status)

    return query.offset(skip).limit(limit).all()


@router.put("/rutas/{ruta_id}", response_model=RutaResponse)
async def update_ruta(
    ruta_id: int,
    ruta_update: RutaUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Update route status"""
    db_ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    for field, value in ruta_update.dict(exclude_unset=True).items():
        setattr(db_ruta, field, value)

    # Update timestamps based on status
    if ruta_update.status == DeliveryStatus.IN_TRANSIT and not db_ruta.started_at:
        db_ruta.started_at = datetime.utcnow()
    elif ruta_update.status == DeliveryStatus.DELIVERED and not db_ruta.completed_at:
        db_ruta.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(db_ruta)
    return db_ruta


# ============================================
# LOCATION TRACKING ENDPOINTS
# ============================================


@router.post("/rutas/{ruta_id}/location", response_model=LocationHistoryResponse)
async def update_location(
    ruta_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Update repartidor location for a route"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    # Save location history
    location_history = LocationHistory(
        ruta_id=ruta_id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
    )
    db.add(location_history)

    # Update repartidor's current location
    repartidor = db.query(Repartidor).filter(Repartidor.id == ruta.repartidor_id).first()
    if repartidor:
        repartidor.latitude = location.latitude
        repartidor.longitude = location.longitude

    db.commit()
    db.refresh(location_history)
    return location_history


@router.get("/rutas/{ruta_id}/locations", response_model=List[LocationHistoryResponse])
async def get_route_locations(
    ruta_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get location history for a route"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    locations = (
        db.query(LocationHistory)
        .filter(LocationHistory.ruta_id == ruta_id)
        .order_by(LocationHistory.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return locations


# ============================================
# STATS ENDPOINTS
# ============================================


@router.get("/stats/repartidor/{repartidor_id}")
async def get_repartidor_stats(
    repartidor_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get delivery statistics for a repartidor"""
    total = db.query(Ruta).filter(Ruta.repartidor_id == repartidor_id).count()
    delivered = (
        db.query(Ruta)
        .filter(
            Ruta.repartidor_id == repartidor_id,
            Ruta.status == DeliveryStatus.DELIVERED,
        )
        .count()
    )
    in_transit = (
        db.query(Ruta)
        .filter(
            Ruta.repartidor_id == repartidor_id,
            Ruta.status == DeliveryStatus.IN_TRANSIT,
        )
        .count()
    )

    return {
        "repartidor_id": repartidor_id,
        "total_deliveries": total,
        "delivered": delivered,
        "in_transit": in_transit,
        "pending": total - delivered - in_transit,
        "success_rate": (delivered / total * 100) if total > 0 else 0,
    }
