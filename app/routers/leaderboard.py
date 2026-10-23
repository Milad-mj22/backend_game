from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.user import User
from app.models.clan import Clan
from app.models.neighborhood import Neighborhood
from app.models.city import City  # اضافه کنید

router = APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"]
)


@router.get("/users")
def get_top_users(limit: int = 20, db: Session = Depends(get_db)):
    """رتبه‌بندی کاربران بر اساس امتیاز"""
    users = (
        db.query(User)
        .filter(User.is_active == True)
        .order_by(desc(User.total_score))
        .limit(limit)
        .all()
    )
    
    return [
        {
            "rank": i + 1,
            "user_id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "total_score": u.total_score,
            "neighborhood_id": u.neighborhood_id,
            "neighborhood_name": u.neighborhood.name if u.neighborhood else None,
            "neighborhood_city": u.neighborhood.city if u.neighborhood else None,
        }
        for i, u in enumerate(users)
    ]


@router.get("/clans")
def get_top_clans(limit: int = 20, db: Session = Depends(get_db)):
    """رتبه‌بندی کلن‌ها"""
    clans = (
        db.query(Clan)
        .filter(Clan.is_active == True)
        .order_by(desc(Clan.total_score))
        .limit(limit)
        .all()
    )
    
    return [
        {
            "rank": i + 1,
            "clan_id": c.id,
            "name": c.name,
            "description": c.description,
            "total_score": c.total_score,
            "member_count": len(c.members),
        }
        for i, c in enumerate(clans)
    ]


@router.get("/neighborhoods")
def get_top_neighborhoods(limit: int = 20, db: Session = Depends(get_db)):
    """رتبه‌بندی محله‌ها بر اساس مجموع امتیاز کاربران"""
    results = (
        db.query(
            Neighborhood.id,
            Neighborhood.name,
            City.name.label("city_name"),  # ← نام شهر از جدول City
            func.sum(User.total_score).label("total_score"),
            func.count(User.id).label("user_count")
        )
        .join(User, User.neighborhood_id == Neighborhood.id)
        .join(City, City.id == Neighborhood.city_id)  # ← جوین با City
        .group_by(Neighborhood.id, City.name)
        .order_by(desc("total_score"))
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": i + 1,
            "neighborhood_id": r.id,
            "name": r.name,
            "city": r.city_name,  # ← استفاده از city_name
            "total_score": r.total_score or 0,
            "user_count": r.user_count,
        }
        for i, r in enumerate(results)
    ]