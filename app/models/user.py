from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    show_real_name = Column(Boolean, default=False)
    total_score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # ← اضافه شد
    # اتصال به شهر و محله
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=True)
    
    city = relationship("City", backref="users")
    # neighborhood از طریق backref در مدل Neighborhood تعریف شده
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())