"""
Pydantic schemas for service3
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Base item schema"""

    name: str
    description: Optional[str] = None
    status: str = "active"


class ItemCreate(ItemBase):
    """Item creation schema"""

    owner_id: int


class ItemUpdate(BaseModel):
    """Item update schema"""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ItemResponse(ItemBase):
    """Item response schema"""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityBase(BaseModel):
    """Base activity schema"""

    action: str
    details: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Activity creation schema"""

    item_id: int
    user_id: int


class ActivityResponse(ActivityBase):
    """Activity response schema"""

    id: int
    item_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
