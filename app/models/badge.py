import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BadgeType(str, enum.Enum):
    """انواع نشان‌ها"""
    FIRST_ACTIVITY = "first_activity"      # اولین فعالیت
    FIRST_WALK = "first_walk"              # اولین پیاده‌روی
    DISTANCE_10KM = "distance_10km"        # 10 کیلومتر مسافت
    DISTANCE_50KM = "distance_50km"        # 50 کیلومتر مسافت
    STREAK_7DAYS = "streak_7days"          # 7 روز متوالی
    EARLY_BIRD = "early_bird"              # فعالیت صبحگاهی
    NIGHT_OWL = "night_owl"                # فعالیت شبانه


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    badge_type = Column(Enum(BadgeType), nullable=False)
    
    # دوره‌ای بودن (طبق سند)
    is_periodic = Column(Integer, default=0)  # 0: دائمی، 1: دوره‌ای
    period_days = Column(Integer, default=0)  # طول دوره (روز)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserBadge(Base):
    """جدول واسط: نشان‌های کسب‌شده توسط کاربر"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # برای نشان‌های دوره‌ای
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", backref="user_badges")
    badge = relationship("Badge", backref="user_badges")