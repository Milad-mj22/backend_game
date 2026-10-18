from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Neighborhood(Base):
    __tablename__ = "neighborhoods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, index=True)
    
    # مرز محله به صورت JSON ذخیره می‌شود
    # فرمت: [{"lat": 32.65, "lng": 51.67}, {"lat": 32.66, "lng": 51.68}, ...]
    polygon = Column(Text, nullable=True)  # JSON string
    
    # مرکز محله (برای نمایش marker)
    center_lat = Column(String, nullable=True)
    center_lng = Column(String, nullable=True)
    
    # آمار
    total_score = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    city = relationship("City", back_populates="neighborhoods")
    users = relationship("User", backref="neighborhood")