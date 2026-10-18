from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Schema پایه
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    show_real_name: bool = False


# Schema برای ثبت‌نام (ورودی)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


# Schema برای ورود (Login)
class UserLogin(BaseModel):
    username: str
    password: str

class UserCityUpdate(BaseModel):
    city_id: int


# برای به‌روزرسانی محله کاربر
class UserNeighborhoodUpdate(BaseModel):
    neighborhood_id: int

class UserResponse(UserBase):
    id: int
    total_score: int
    is_active: bool
    is_admin: bool  # ← اضافه شد
    city_id: Optional[int] = None
    neighborhood_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Schema برای Token
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema برای محتوای Token
class TokenData(BaseModel):
    username: Optional[str] = None