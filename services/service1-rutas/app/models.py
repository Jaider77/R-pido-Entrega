"""
SQLAlchemy models for routes service
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DeliveryStatus(str, Enum):
    """Delivery status enum"""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Repartidor(Base):
    """Repartidor (delivery person) model"""

    __tablename__ = "repartidores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # bike, motorcycle, car
    license_plate = Column(String(20), nullable=True, unique=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Repartidor(id={self.id}, user_id={self.user_id}, vehicle={self.vehicle_type})>"


class Ruta(Base):
    """Route model"""

    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    repartidor_id = Column(Integer, nullable=False, index=True)
    delivery_id = Column(Integer, nullable=False, index=True)
    origin_latitude = Column(Float, nullable=False)
    origin_longitude = Column(Float, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    estimated_distance_km = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    status = Column(
        SQLEnum(DeliveryStatus),
        default=DeliveryStatus.PENDING,
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Ruta(id={self.id}, status={self.status}, repartidor_id={self.repartidor_id})>"


class LocationHistory(Base):
    """Location tracking history"""

    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LocationHistory(id={self.id}, ruta_id={self.ruta_id})>"
