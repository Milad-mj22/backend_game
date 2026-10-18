from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CityBase(BaseModel):
    name: str
    province: Optional[str] = None
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None
    default_zoom: int = 12


class CityCreate(CityBase):
    pass


class CityResponse(CityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True