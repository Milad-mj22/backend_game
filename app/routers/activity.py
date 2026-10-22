from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services import activity_service
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """ثبت فعالیت جدید (نیاز به احراز هویت)"""
    return activity_service.create_activity(db, current_user, activity)


@router.get("/me", response_model=List[ActivityResponse])
def get_my_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """گرفتن لیست فعالیت‌های من"""
    return activity_service.get_user_activities(db, current_user.id, skip, limit)


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """گرفتن یک فعالیت خاص"""
    activity = activity_service.get_activity_by_id(db, activity_id, current_user.id)
    if not activity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="فعالیت یافت نشد")
    return activity



from app.schemas.activity import ActivityCreate, ActivityResponse, StepActivityCreate


@router.post("/step", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_step_activity(
    activity: StepActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """ثبت فعالیت خودکار بر اساس قدم‌های سنسور"""
    return activity_service.create_step_activity(db, current_user, activity)