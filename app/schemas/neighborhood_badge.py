from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.neighborhood_badge import (
    NeighborhoodBadgeType, DailyBadgeType, NeighborhoodCategory
)


class NeighborhoodBadgeResponse(BaseModel):
    id: int
    badge_type: NeighborhoodBadgeType
    user_id: int
    username: str
    display_name: str
    score_at_earn: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class DailyBadgeResponse(BaseModel):
    id: int
    badge_type: DailyBadgeType
    metric_value: int
    date: datetime


class NeighborhoodUserResponse(BaseModel):
    """اطلاعات کاربر در محله"""
    id: int
    username: str
    display_name: str
    total_score: int
    rank: int


class MyNeighborhoodResponse(BaseModel):
    """اطلاعات کامل محله کاربر"""
    id: int
    name: str
    city_id: Optional[int]
    city_name: Optional[str]
    total_score: int
    user_count: int
    rank_in_city: int
    category: Optional[NeighborhoodCategory]
    
    # شهردار (کاربر با بیشترین امتیاز)
    mayor: Optional[NeighborhoodUserResponse]
    
    # لیست کاربران (Top 10)
    top_users: List[NeighborhoodUserResponse]
    
    # نشان‌های دوره‌ای
    badges: List[NeighborhoodBadgeResponse]
    
    # نشان‌های روزانه
    daily_badges: List[DailyBadgeResponse]
    
    # جایگاه کاربر فعلی
    my_rank: Optional[int]