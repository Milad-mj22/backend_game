import enum
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ActivityType(str, enum.Enum):
    WALKING = "walking"
    RUNNING = "running"
    HIKING = "hiking"
    CYCLING = "cycling"


ACTIVITY_MULTIPLIERS = {
    ActivityType.WALKING: 1.0,
    ActivityType.RUNNING: 1.5,
    ActivityType.HIKING: 1.8,
    ActivityType.CYCLING: 1.3,
}


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(Enum(ActivityType), nullable=False)

    distance_km = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    base_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)

    # === فیلدهای جدید برای ثبت خودکار ===
    steps = Column(Integer, nullable=True)
    start_lat = Column(Float, nullable=True)
    start_lng = Column(Float, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lng = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="activities")