from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.neighborhood import (
    NeighborhoodCreate, NeighborhoodUpdate, NeighborhoodResponse
)
from app.services import neighborhood_service
from app.core.dependencies import get_current_active_user, get_current_admin
from app.models.user import User

router = APIRouter(
    prefix="/neighborhoods",
    tags=["Neighborhoods"]
)


# ============ PUBLIC ============
@router.get("/", response_model=List[NeighborhoodResponse])
def list_neighborhoods(
    city_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    neighborhoods = neighborhood_service.get_all_neighborhoods(db, city_id)
    return [neighborhood_service._to_response(n) for n in neighborhoods]


@router.get("/{neighborhood_id}", response_model=NeighborhoodResponse)
def get_neighborhood(neighborhood_id: int, db: Session = Depends(get_db)):
    db_neighborhood = neighborhood_service.get_neighborhood_by_id(db, neighborhood_id)
    if not db_neighborhood:
        raise HTTPException(status_code=404, detail="محله یافت نشد")
    return neighborhood_service._to_response(db_neighborhood)


# ============ ADMIN ONLY ============
@router.post("/", response_model=NeighborhoodResponse, status_code=status.HTTP_201_CREATED)
def create_neighborhood(
    neighborhood: NeighborhoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ← فقط ادمین
):
    """ساخت محله جدید (فقط ادمین)"""
    return neighborhood_service.create_neighborhood(db, neighborhood)


@router.put("/{neighborhood_id}", response_model=NeighborhoodResponse)
def update_neighborhood(
    neighborhood_id: int,
    data: NeighborhoodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ← فقط ادمین
):
    """ویرایش محله (فقط ادمین)"""
    return neighborhood_service.update_neighborhood(db, neighborhood_id, data)


@router.delete("/{neighborhood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_neighborhood(
    neighborhood_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ← فقط ادمین
):
    """حذف محله (فقط ادمین)"""
    neighborhood_service.delete_neighborhood(db, neighborhood_id)
    return None