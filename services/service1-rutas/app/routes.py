"""
Routes and delivery endpoints
"""

from datetime import datetime, timezone
from typing import List, Optional

import httpx
from app.config import settings
from app.database import get_db
from app.models import DeliveryStatus, LocationHistory, Repartidor, Ruta, RutaStatusHistory
from app.schemas import (
    LocationHistoryResponse,
    LocationUpdate,
    RepartidorCreate,
    RepartidorResponse,
    RepartidorUpdate,
    RutaCreate,
    RutaResponse,
    RutaStatusHistoryResponse,
    RutaUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from geopy.distance import geodesic
from sqlalchemy import or_
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
            payload = response.json().get("payload")
            if not isinstance(payload, dict):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            # include the raw token so downstream handlers can fetch user info
            payload["token"] = token
            return payload
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )


async def geocode_address(address: str) -> tuple[Optional[float], Optional[float]]:
    """Geocode an address using Nominatim (OpenStreetMap). Returns (lat, lon) or (None, None)."""
    if not address:
        return None, None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "Rapido-Entrega/1.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    item = data[0]
                    return float(item.get("lat")), float(item.get("lon"))
    except Exception:
        # ignore geocoding errors and fall back to None
        return None, None
    return None, None


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
    """Create a new repartidor profile for the authenticated repartidor user"""
    if auth.get("role") != "repartidor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with repartidor role can create a repartidor profile",
        )

    user_id = auth.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token payload",
        )

    existing = db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repartidor already exists for this user",
        )

    db_repartidor = Repartidor(user_id=user_id, **repartidor.model_dump())
    db.add(db_repartidor)
    db.commit()
    db.refresh(db_repartidor)
    return db_repartidor


@router.get("/repartidores/me", response_model=RepartidorResponse)
async def get_my_repartidor(
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get repartidor profile for the authenticated repartidor user"""
    user_id = auth.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token payload",
        )

    repartidor = db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
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

    for field, value in repartidor_update.model_dump(exclude_unset=True).items():
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
    repartidor_id = ruta.repartidor_id
    creator_user_id = auth.get("sub")
    try:
        creator_user_id = int(creator_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token payload",
        )

    if repartidor_id is None and auth.get("role") == "repartidor":
        user_id = creator_user_id
        repartidor = db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
        if repartidor:
            repartidor_id = repartidor.id

    db_repartidor = None
    if repartidor_id is not None:
        db_repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
        if not db_repartidor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repartidor not found",
            )

    # Calculate distance if lat/lng available; otherwise attempt geocoding from addresses
    origin_lat = getattr(ruta, "origin_latitude", None)
    origin_lng = getattr(ruta, "origin_longitude", None)
    dest_lat = getattr(ruta, "destination_latitude", None)
    dest_lng = getattr(ruta, "destination_longitude", None)

    # Try geocoding if coordinates are missing but addresses are provided
    if (origin_lat is None or origin_lng is None) and getattr(ruta, "origin_address", None):
        o_lat, o_lng = await geocode_address(ruta.origin_address)
        if o_lat is not None and o_lng is not None:
            origin_lat, origin_lng = o_lat, o_lng

    if (dest_lat is None or dest_lng is None) and getattr(ruta, "destination_address", None):
        d_lat, d_lng = await geocode_address(ruta.destination_address)
        if d_lat is not None and d_lng is not None:
            dest_lat, dest_lng = d_lat, d_lng

    distance_km = None
    estimated_time = None
    if (
        origin_lat is not None
        and origin_lng is not None
        and dest_lat is not None
        and dest_lng is not None
    ):
        try:
            origin = (origin_lat, origin_lng)
            destination = (dest_lat, dest_lng)
            distance_km = geodesic(origin, destination).kilometers
            # Estimate time (assuming average speed of 30 km/h)
            estimated_time = int((distance_km / 30) * 60)
        except Exception:
            distance_km = None
            estimated_time = None

    route_data = ruta.model_dump(exclude_none=True)
    # include any geocoded coordinates if available
    if origin_lat is not None and origin_lng is not None:
        route_data["origin_latitude"] = origin_lat
        route_data["origin_longitude"] = origin_lng
    if dest_lat is not None and dest_lng is not None:
        route_data["destination_latitude"] = dest_lat
        route_data["destination_longitude"] = dest_lng

    if repartidor_id is not None:
        route_data["repartidor_id"] = repartidor_id
    route_data["created_by_user_id"] = creator_user_id

    db_ruta = Ruta(
        **route_data,
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

    user_role = auth.get("role")
    if user_role == "repartidor":
        user_id = auth.get("sub")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            user_id = None
        if user_id is not None:
            repartidor = db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
            if repartidor:
                query = query.filter(
                    or_(
                        Ruta.repartidor_id == repartidor.id,
                        Ruta.repartidor_id.is_(None),
                    )
                )
            else:
                return []
    elif user_role == "user":
        user_id = auth.get("sub")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            user_id = None
        if user_id is not None:
            query = query.filter(Ruta.created_by_user_id == user_id)

    if user_role != "repartidor" and repartidor_id is not None:
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

    previous_status = db_ruta.status

    # Ensure repartidor updating is authorized
    if auth.get("role") == "repartidor":
        user_id = auth.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user id in token payload",
            )

        current_repartidor = db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
        if not current_repartidor or (
            db_ruta.repartidor_id is not None and current_repartidor.id != db_ruta.repartidor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado para actualizar esta ruta",
            )
        if db_ruta.repartidor_id is None and ruta_update.status in (
            DeliveryStatus.ASSIGNED,
            DeliveryStatus.IN_TRANSIT,
        ):
            db_ruta.repartidor_id = current_repartidor.id

    for field, value in ruta_update.model_dump(exclude_unset=True).items():
        setattr(db_ruta, field, value)

    # Prepare status history and last-changed metadata
    if ruta_update.status and ruta_update.status != previous_status:
        changed_by_user_id = auth.get("sub")
        try:
            changed_by_user_id = int(changed_by_user_id)
        except (TypeError, ValueError):
            changed_by_user_id = 0

        changed_by_repartidor_id = None
        changed_by_name = None
        changed_by_plate = None

        # If the actor is a repartidor, populate repartidor info
        if auth.get("role") == "repartidor":
            if "current_repartidor" not in locals():
                user_id = auth.get("sub")
                try:
                    user_id = int(user_id)
                except (TypeError, ValueError):
                    user_id = None
                if user_id:
                    current_repartidor = (
                        db.query(Repartidor).filter(Repartidor.user_id == user_id).first()
                    )
            if current_repartidor:
                changed_by_repartidor_id = current_repartidor.id
                changed_by_plate = current_repartidor.license_plate

        # Try to fetch full name from auth service when token present
        token = auth.get("token")
        if token:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{settings.auth_service_url}/api/auth/me",
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    if resp.status_code == 200:
                        changed_by_name = resp.json().get("full_name")
            except httpx.HTTPError:
                changed_by_name = None

        status_history = RutaStatusHistory(
            ruta_id=ruta_id,
            previous_status=previous_status,
            new_status=ruta_update.status,
            changed_by_user_id=changed_by_user_id,
            changed_by_repartidor_id=changed_by_repartidor_id,
            changed_by_name=changed_by_name,
            changed_by_plate=changed_by_plate,
        )
        db.add(status_history)

        # also store last-changed metadata on the ruta for quick listing
        db_ruta.last_changed_by_name = changed_by_name
        db_ruta.last_changed_by_plate = changed_by_plate

    # Update timestamps based on status
    if ruta_update.status == DeliveryStatus.IN_TRANSIT and not db_ruta.started_at:
        db_ruta.started_at = datetime.now(timezone.utc)
    elif ruta_update.status == DeliveryStatus.DELIVERED and not db_ruta.completed_at:
        db_ruta.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_ruta)
    return db_ruta


@router.get("/rutas/{ruta_id}/status-history", response_model=List[RutaStatusHistoryResponse])
async def get_route_status_history(
    ruta_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_auth_token),
):
    """Get the status history for a route"""
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    history = (
        db.query(RutaStatusHistory)
        .filter(RutaStatusHistory.ruta_id == ruta_id)
        .order_by(RutaStatusHistory.changed_at.desc())
        .all()
    )
    return history


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
