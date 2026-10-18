from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.city import City
from app.schemas.city import CityCreate


def get_all_cities(db: Session):
    return db.query(City).all()


def get_city_by_id(db: Session, city_id: int):
    return db.query(City).filter(City.id == city_id).first()


def get_city_by_name(db: Session, name: str):
    return db.query(City).filter(City.name == name).first()


def create_city(db: Session, city: CityCreate):
    if get_city_by_name(db, city.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این شهر قبلاً ثبت شده است"
        )
    
    db_city = City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def seed_cities(db: Session):
    """ساخت شهرهای پیش‌فرض (اصفهان و تهران)"""
    default_cities = [
        {
            "name": "اصفهان",
            "province": "اصفهان",
            "center_lat": "32.6546",
            "center_lng": "51.6680",
            "default_zoom": 12,
        },
        {
            "name": "تهران",
            "province": "تهران",
            "center_lat": "35.6892",
            "center_lng": "51.3890",
            "default_zoom": 12,
        },
    ]
    
    for city_data in default_cities:
        existing = get_city_by_name(db, city_data["name"])
        if not existing:
            db.add(City(**city_data))
    
    db.commit()