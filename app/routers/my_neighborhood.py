from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services import neighborhood_stats_service

router = APIRouter(
    prefix="/my-neighborhood",
    tags=["My Neighborhood"]
)


@router.get("/")
def get_my_neighborhood(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """اطلاعات کامل محله کاربر"""
    info = neighborhood_stats_service.get_my_neighborhood_info(db, current_user)
    if not info:
        raise HTTPException(
            status_code=404,
            detail="شما هنوز محله‌ای انتخاب نکرده‌اید"
        )
    return info


@router.post("/recalculate-daily/{city_id}")
def recalculate_daily_badges(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    محاسبه مجدد نشان‌های روزانه (فقط برای تست).
    در پروداکشن، این کار باید روزانه با Cron Job انجام شود.
    """
    neighborhood_stats_service.calculate_daily_badges(db, city_id)
    return {"message": "نشان‌های روزانه محاسبه شد"}