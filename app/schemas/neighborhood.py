from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class Coordinate(BaseModel):
    lat: float
    lng: float


class NeighborhoodBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    city_id: Optional[int] = None
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None


class NeighborhoodCreate(NeighborhoodBase):
    polygon: Optional[List[Coordinate]] = None  # آرایه‌ای از نقاط


class NeighborhoodUpdate(BaseModel):
    name: Optional[str] = None
    polygon: Optional[List[Coordinate]] = None
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None


class NeighborhoodResponse(NeighborhoodBase):
    id: int
    polygon: Optional[List[Coordinate]] = None
    total_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class NeighborhoodSimple(BaseModel):
    """برای لیست‌های ساده"""
    id: int
    name: str
    city_id: Optional[int] = None

    class Config:
        from_attributes = True