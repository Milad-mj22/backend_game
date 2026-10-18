from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.neighborhood import Neighborhood
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate):
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نام کاربری قبلاً استفاده شده است"
        )
    
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        display_name=user.display_name or user.username,
        show_real_name=user.show_real_name,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def set_user_neighborhood(db: Session, user: User, neighborhood_id: int):
    """اتصال کاربر به یک محله"""
    neighborhood = db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()
    if not neighborhood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محله یافت نشد"
        )
    
    user.neighborhood_id = neighborhood_id
    db.commit()
    db.refresh(user)
    return user