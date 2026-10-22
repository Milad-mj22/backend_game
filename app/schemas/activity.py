from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    activity_type: ActivityType
    distance_km: float = Field(..., gt=0, le=500)
    duration_minutes: int = Field(..., gt=0, le=1440)


class StepActivityCreate(BaseModel):
    """ثبت فعالیت خودکار از سنسورها"""
    activity_type: ActivityType = ActivityType.WALKING
    steps: int = Field(..., gt=0, le=100000)
    distance_km: float = Field(..., gt=0, le=500)
    duration_minutes: int = Field(..., gt=0, le=1440)
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float


class ActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: ActivityType
    distance_km: float
    duration_minutes: int
    base_score: float
    final_score: float
    steps: Optional[int] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True