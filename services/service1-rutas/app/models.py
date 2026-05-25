"""
SQLAlchemy models for routes service
"""

from datetime import datetime, timezone
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
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Repartidor(id={self.id}, user_id={self.user_id}, vehicle={self.vehicle_type})>"


class Ruta(Base):
    """Route model"""

    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    repartidor_id = Column(Integer, nullable=True, index=True)
    delivery_id = Column(Integer, nullable=False, index=True)
    created_by_user_id = Column(Integer, nullable=False, index=True)
    origin_latitude = Column(Float, nullable=True)
    origin_longitude = Column(Float, nullable=True)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)
    origin_address = Column(Text, nullable=True)
    destination_address = Column(Text, nullable=True)
    estimated_distance_km = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    status = Column(
        SQLEnum(DeliveryStatus),
        default=DeliveryStatus.PENDING,
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    last_changed_by_name = Column(String(150), nullable=True)
    last_changed_by_plate = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

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
    timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<LocationHistory(id={self.id}, ruta_id={self.ruta_id})>"


class RutaStatusHistory(Base):
    """Route status history record"""

    __tablename__ = "ruta_status_history"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, nullable=False, index=True)
    previous_status = Column(SQLEnum(DeliveryStatus), nullable=False)
    new_status = Column(SQLEnum(DeliveryStatus), nullable=False)
    changed_by_user_id = Column(Integer, nullable=False)
    changed_by_repartidor_id = Column(Integer, nullable=True)
    changed_by_name = Column(String(150), nullable=True)
    changed_by_plate = Column(String(50), nullable=True)
    changed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return (
            f"<RutaStatusHistory(id={self.id}, ruta_id={self.ruta_id}, "
            f"{self.previous_status}->{self.new_status}, by={self.changed_by_user_id})>"
        )
