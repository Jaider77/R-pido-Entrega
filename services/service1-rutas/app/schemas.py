"""
Pydantic schemas for routes service
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeliveryStatus(str, Enum):
    """Delivery status"""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class RepartidorBase(BaseModel):
    """Base repartidor schema"""

    user_id: int
    phone: str
    vehicle_type: str = Field(description="bike, motorcycle, car")
    license_plate: Optional[str] = None


class RepartidorCreate(RepartidorBase):
    """Repartidor creation schema"""

    pass


class RepartidorUpdate(BaseModel):
    """Repartidor update schema"""

    phone: Optional[str] = None
    vehicle_type: Optional[str] = None
    license_plate: Optional[str] = None
    is_active: Optional[bool] = None


class RepartidorResponse(RepartidorBase):
    """Repartidor response schema"""

    id: int
    latitude: Optional[float]
    longitude: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationUpdate(BaseModel):
    """Location update schema"""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: Optional[float] = None


class RutaBase(BaseModel):
    """Base route schema"""

    repartidor_id: int
    delivery_id: int
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float


class RutaCreate(RutaBase):
    """Route creation schema"""

    notes: Optional[str] = None


class RutaUpdate(BaseModel):
    """Route update schema"""

    status: Optional[DeliveryStatus] = None
    notes: Optional[str] = None


class RutaResponse(RutaBase):
    """Route response schema"""

    id: int
    estimated_distance_km: Optional[float]
    estimated_duration_minutes: Optional[int]
    status: DeliveryStatus
    notes: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class LocationHistoryResponse(BaseModel):
    """Location history response"""

    id: int
    ruta_id: int
    latitude: float
    longitude: float
    accuracy: Optional[float]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
