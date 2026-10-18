from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_access_token
from app.services import user_service

# آدرس Login (برای مستندات Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """گرفتن کاربر فعلی از Token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="اعتبارسنجی ناموفق",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = user_service.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """بررسی فعال بودن کاربر"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="کاربر غیرفعال است")
    return current_user




def get_current_admin(current_user = Depends(get_current_active_user)):
    """فقط ادمین‌ها اجازه دسترسی دارند"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی ادمین ندارید"
        )
    return current_user