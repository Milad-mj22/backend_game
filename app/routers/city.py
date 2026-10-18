from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.city import CityCreate, CityResponse
from app.services import city_service
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/cities",
    tags=["Cities"]
)


@router.get("/", response_model=List[CityResponse])
def list_cities(db: Session = Depends(get_db)):
    """لیست همه شهرها (عمومی)"""
    return city_service.get_all_cities(db)


@router.get("/{city_id}", response_model=CityResponse)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = city_service.get_city_by_id(db, city_id)
    if not city:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="شهر یافت نشد")
    return city


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(
    city: CityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """ساخت شهر جدید (فقط ادمین - در آینده محدود می‌شود)"""
    return city_service.create_city(db, city)