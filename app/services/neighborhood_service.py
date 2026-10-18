import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.neighborhood import Neighborhood
from app.schemas.neighborhood import NeighborhoodCreate


def get_all_neighborhoods(db: Session, city_id: int = None):
    query = db.query(Neighborhood)
    if city_id:
        query = query.filter(Neighborhood.city_id == city_id)
    return query.all()


def get_neighborhood_by_id(db: Session, neighborhood_id: int):
    return db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()


def get_neighborhood_by_name(db: Session, name: str, city_id: int = None):
    query = db.query(Neighborhood).filter(Neighborhood.name == name)
    if city_id:
        query = query.filter(Neighborhood.city_id == city_id)
    return query.first()


def _serialize_polygon(polygon):
    """تبدیل آرایه نقاط به JSON String"""
    if polygon is None:
        return None
    return json.dumps([{"lat": p.lat, "lng": p.lng} for p in polygon])


def _deserialize_polygon(polygon_str):
    """تبدیل JSON String به آرایه"""
    if not polygon_str:
        return None
    try:
        return json.loads(polygon_str)
    except (json.JSONDecodeError, TypeError):
        return None


def _to_response(neighborhood: Neighborhood):
    """تبدیل مدل به dict برای پاسخ"""
    return {
        "id": neighborhood.id,
        "name": neighborhood.name,
        "city_id": neighborhood.city_id,
        "center_lat": neighborhood.center_lat,
        "center_lng": neighborhood.center_lng,
        "polygon": _deserialize_polygon(neighborhood.polygon),
        "total_score": neighborhood.total_score or 0,
        "created_at": neighborhood.created_at,
    }


def create_neighborhood(db: Session, neighborhood: NeighborhoodCreate):
    if get_neighborhood_by_name(db, neighborhood.name, neighborhood.city_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این محله قبلاً در این شهر ثبت شده است"
        )
    
    db_neighborhood = Neighborhood(
        name=neighborhood.name,
        city_id=neighborhood.city_id,
        center_lat=neighborhood.center_lat,
        center_lng=neighborhood.center_lng,
        polygon=_serialize_polygon(neighborhood.polygon),
    )
    db.add(db_neighborhood)
    db.commit()
    db.refresh(db_neighborhood)
    return _to_response(db_neighborhood)


def update_neighborhood(db: Session, neighborhood_id: int, data):
    db_neighborhood = get_neighborhood_by_id(db, neighborhood_id)
    if not db_neighborhood:
        raise HTTPException(status_code=404, detail="محله یافت نشد")
    
    if data.name is not None:
        db_neighborhood.name = data.name
    if data.polygon is not None:
        db_neighborhood.polygon = _serialize_polygon(data.polygon)
    if data.center_lat is not None:
        db_neighborhood.center_lat = data.center_lat
    if data.center_lng is not None:
        db_neighborhood.center_lng = data.center_lng
    
    db.commit()
    db.refresh(db_neighborhood)
    return _to_response(db_neighborhood)


def delete_neighborhood(db: Session, neighborhood_id: int):
    db_neighborhood = get_neighborhood_by_id(db, neighborhood_id)
    if not db_neighborhood:
        raise HTTPException(status_code=404, detail="محله یافت نشد")
    db.delete(db_neighborhood)
    db.commit()
    return True