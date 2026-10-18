from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.badge import UserBadge

router = APIRouter(
    prefix="/badges",
    tags=["Badges"]
)


@router.get("/me")
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """گرفتن نشان‌های کاربر لاگین‌شده"""
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    return [
        {
            "id": ub.id,
            "badge_id": ub.badge_id,
            "earned_at": ub.earned_at,
            "badge": {
                "name": ub.badge.name,
                "description": ub.badge.description,
            }
        }
        for ub in user_badges
    ]