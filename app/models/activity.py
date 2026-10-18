import enum
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ActivityType(str, enum.Enum):
    """انواع فعالیت‌ها طبق سند"""
    WALKING = "walking"        # پیاده‌روی
    RUNNING = "running"        # دویدن
    HIKING = "hiking"          # کوه‌پیمایی
    CYCLING = "cycling"        # دوچرخه‌سواری


# ضرایب امتیازدهی بر اساس سختی فعالیت (طبق سند)
ACTIVITY_MULTIPLIERS = {
    ActivityType.WALKING: 1.0,    # ضریب پایه
    ActivityType.RUNNING: 1.5,    # سخت‌تر از پیاده‌روی
    ActivityType.HIKING: 1.8,     # سخت‌تر از دویدن
    ActivityType.CYCLING: 1.3,    # بین پیاده‌روی و دویدن
}


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    
    # داده‌های فعالیت
    distance_km = Column(Float, nullable=False)        # مسافت (کیلومتر)
    duration_minutes = Column(Integer, nullable=False)  # مدت زمان (دقیقه)
    
    # امتیاز محاسبه‌شده
    base_score = Column(Float, nullable=False)      # امتیاز خام
    final_score = Column(Float, nullable=False)     # امتیاز نهایی (با ضریب)
    
    # زمان
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ارتباط با کاربر
    user = relationship("User", backref="activities")