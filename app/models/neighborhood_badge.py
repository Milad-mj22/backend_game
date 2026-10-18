import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NeighborhoodBadgeType(str, enum.Enum):
    """نشان‌های دوره‌ای محله (طبق سند)"""
    SULTAN = "sultan"               # سلطان
    CONQUEROR = "conqueror"          # فاتح
    MERCHANT = "merchant"            # تاجر
    REBEL = "rebel"                  # لثون/یاغی
    GODFATHER = "godfather"          # پدرخوانده
    WANDERER = "wanderer"            # پهلوان دور گرد
    EXPLORER = "explorer"            # کریستف کلمب / ماجراجو


class DailyBadgeType(str, enum.Enum):
    """نشان‌های روزانه محله"""
    BLOODIEST = "bloodiest"          # خونین‌ترین
    MOST_ABANDONED = "most_abandoned"  # متروک‌ترین
    HOTTEST = "hottest"              # داغ‌ترین
    NIGHT_OWL = "night_owl"          # شب‌زنده‌دارترین
    MOST_COMPETITIVE = "most_competitive"  # رقابتی‌ترین


class NeighborhoodCategory(str, enum.Enum):
    """دسته‌بندی محله‌ها"""
    BLOODY = "bloody"      # خونین
    HARD = "hard"          # سخت
    ABANDONED = "abandoned"  # متروک


class NeighborhoodBadge(Base):
    """نشان‌های دوره‌ای محله"""
    __tablename__ = "neighborhood_badges"

    id = Column(Integer, primary_key=True, index=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_type = Column(Enum(NeighborhoodBadgeType), nullable=False)
    
    # دوره
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)  # آیا در دوره فعلی فعال است؟
    
    # اطلاعات اضافی (مثلاً امتیاز در زمان اهدا)
    score_at_earn = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    neighborhood = relationship("Neighborhood", backref="badges")
    user = relationship("User", backref="neighborhood_badges")


class DailyNeighborhoodBadge(Base):
    """نشان‌های روزانه محله"""
    __tablename__ = "daily_neighborhood_badges"

    id = Column(Integer, primary_key=True, index=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=False, index=True)
    badge_type = Column(Enum(DailyBadgeType), nullable=False)
    
    # تاریخ (روز)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # مقدار شاخص
    metric_value = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    neighborhood = relationship("Neighborhood", backref="daily_badges")