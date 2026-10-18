from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token, UserNeighborhoodUpdate, UserCityUpdate
from app.services import user_service
from app.core.security import create_access_token
from app.core.config import settings
from app.core.dependencies import get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """ثبت‌نام کاربر جدید"""
    return user_service.create_user(db, user)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ورود کاربر و دریافت Token"""
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_active_user)):
    """گرفتن اطلاعات کاربر لاگین‌شده"""
    return current_user



@router.put("/me/neighborhood", response_model=UserResponse)
def set_neighborhood(
    data: UserNeighborhoodUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """انتخاب یا تغییر محله کاربر"""
    return user_service.set_user_neighborhood(db, current_user, data.neighborhood_id)




@router.put("/me/city", response_model=UserResponse)
def set_city(
    data: UserCityUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """انتخاب یا تغییر شهر کاربر"""
    from app.services import city_service
    city = city_service.get_city_by_id(db, data.city_id)
    if not city:
        raise HTTPException(status_code=404, detail="شهر یافت نشد")
    
    current_user.city_id = data.city_id
    current_user.neighborhood_id = None  # ریست محله
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/neighborhood", response_model=UserResponse)
def set_neighborhood(
    data: UserNeighborhoodUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """انتخاب یا تغییر محله کاربر"""
    return user_service.set_user_neighborhood(db, current_user, data.neighborhood_id)