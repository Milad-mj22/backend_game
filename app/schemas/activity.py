from pydantic import BaseModel, Field
from datetime import datetime
from app.models.activity import ActivityType


# Schema برای ثبت فعالیت (ورودی)
class ActivityCreate(BaseModel):
    activity_type: ActivityType
    distance_km: float = Field(..., gt=0, le=500, description="مسافت به کیلومتر")
    duration_minutes: int = Field(..., gt=0, le=1440, description="مدت زمان به دقیقه")


# Schema برای خروجی
class ActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: ActivityType
    distance_km: float
    duration_minutes: int
    base_score: float
    final_score: float
    created_at: datetime

    class Config:
        from_attributes = True