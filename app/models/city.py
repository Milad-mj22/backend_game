from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    province = Column(String, nullable=True)
    
    # مرکز نقشه (برای زوم اولیه)
    center_lat = Column(String, nullable=True)
    center_lng = Column(String, nullable=True)
    default_zoom = Column(Integer, default=12)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    neighborhoods = relationship("Neighborhood", back_populates="city")