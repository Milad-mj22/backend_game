from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.activity import Activity, ActivityType, ACTIVITY_MULTIPLIERS
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.services import badge_service


def calculate_score(activity_type: ActivityType, distance_km: float, duration_minutes: int) -> tuple[float, float]:
    base_score = (distance_km * 10) + (duration_minutes / 2)
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_type, 1.0)
    final_score = base_score * multiplier
    return round(base_score, 2), round(final_score, 2)


def create_activity(db: Session, user: User, activity: ActivityCreate) -> Activity:
    base_score, final_score = calculate_score(
        activity.activity_type,
        activity.distance_km,
        activity.duration_minutes
    )
    
    db_activity = Activity(
        user_id=user.id,
        activity_type=activity.activity_type,
        distance_km=activity.distance_km,
        duration_minutes=activity.duration_minutes,
        base_score=base_score,
        final_score=final_score
    )
    db.add(db_activity)
    user.total_score += int(final_score)
    db.commit()
    db.refresh(db_activity)
    
    # بررسی و اهدای نشان‌ها
    badge_service.check_and_award_badges(db, user, db_activity)
    
    return db_activity



def get_user_activities(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """گرفتن لیست فعالیت‌های یک کاربر"""
    return (
        db.query(Activity)
        .filter(Activity.user_id == user_id)
        .order_by(Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_activity_by_id(db: Session, activity_id: int, user_id: int):
    """گرفتن یک فعالیت خاص (فقط اگر متعلق به کاربر باشد)"""
    return (
        db.query(Activity)
        .filter(Activity.id == activity_id, Activity.user_id == user_id)
        .first()
    )