from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User
from app.models.neighborhood import Neighborhood
from app.models.activity import Activity
from app.models.neighborhood_badge import (
    NeighborhoodBadge, DailyNeighborhoodBadge,
    NeighborhoodBadgeType, DailyBadgeType, NeighborhoodCategory
)


def get_mayor(db: Session, neighborhood_id: int):
    """شهردار = کاربر با بیشترین امتیاز در محله"""
    return (
        db.query(User)
        .filter(User.neighborhood_id == neighborhood_id, User.is_active == True)
        .order_by(desc(User.total_score))
        .first()
    )


def get_top_users(db: Session, neighborhood_id: int, limit: int = 10):
    """Top کاربران محله"""
    users = (
        db.query(User)
        .filter(User.neighborhood_id == neighborhood_id, User.is_active == True)
        .order_by(desc(User.total_score))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name or u.username,
            "total_score": u.total_score,
            "rank": i + 1,
        }
        for i, u in enumerate(users)
    ]


def get_user_rank_in_neighborhood(db: Session, user_id: int, neighborhood_id: int):
    """رتبه کاربر در محله"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    rank = (
        db.query(func.count(User.id))
        .filter(
            User.neighborhood_id == neighborhood_id,
            User.total_score > user.total_score,
            User.is_active == True
        )
        .scalar()
    )
    return (rank or 0) + 1


def get_neighborhood_rank_in_city(db: Session, neighborhood_id: int, city_id: int):
    """رتبه محله در شهر بر اساس مجموع امتیاز کاربران"""
    # مجموع امتیاز هر محله
    scores = (
        db.query(
            Neighborhood.id,
            func.coalesce(func.sum(User.total_score), 0).label("total")
        )
        .outerjoin(User, User.neighborhood_id == Neighborhood.id)
        .filter(Neighborhood.city_id == city_id)
        .group_by(Neighborhood.id)
        .order_by(desc("total"))
        .all()
    )
    for i, s in enumerate(scores):
        if s.id == neighborhood_id:
            return i + 1
    return 0


def calculate_neighborhood_category(db: Session, neighborhood_id: int) -> NeighborhoodCategory:
    """
    محاسبه دسته‌بندی محله بر اساس فعالیت ۷ روز اخیر.
    - خونین: رقابت بالا (تعداد زیاد جابه‌جایی رتبه)
    - سخت: رقابت شدید
    - متروک: فعالیت کم
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    activity_count = (
        db.query(func.count(Activity.id))
        .join(User, User.id == Activity.user_id)
        .filter(
            User.neighborhood_id == neighborhood_id,
            Activity.created_at >= seven_days_ago
        )
        .scalar() or 0
    )
    
    user_count = (
        db.query(func.count(User.id))
        .filter(User.neighborhood_id == neighborhood_id, User.is_active == True)
        .scalar() or 0
    )
    
    # میانگین فعالیت هر کاربر
    if user_count == 0:
        return NeighborhoodCategory.ABANDONED
    
    avg_activity = activity_count / user_count
    
    if avg_activity < 1:
        return NeighborhoodCategory.ABANDONED
    elif avg_activity < 5:
        return NeighborhoodCategory.HARD
    else:
        return NeighborhoodCategory.BLOODY


def calculate_daily_badges(db: Session, city_id: int):
    """
    محاسبه نشان‌های روزانه برای همه محله‌های یک شهر.
    این تابع باید روزانه اجرا شود (Cron Job).
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    neighborhoods = (
        db.query(Neighborhood)
        .filter(Neighborhood.city_id == city_id)
        .all()
    )
    
    if not neighborhoods:
        return
    
    # پاک کردن نشان‌های امروز (اگر قبلاً محاسبه شده)
    db.query(DailyNeighborhoodBadge).filter(
        DailyNeighborhoodBadge.date >= today,
        DailyNeighborhoodBadge.date < tomorrow,
        DailyNeighborhoodBadge.neighborhood_id.in_([n.id for n in neighborhoods])
    ).delete(synchronize_session=False)
    db.commit()
    
    # محاسبه معیارها برای هر محله
    metrics = {}
    for n in neighborhoods:
        # تعداد فعالیت امروز
        activity_count = (
            db.query(func.count(Activity.id))
            .join(User, User.id == Activity.user_id)
            .filter(
                User.neighborhood_id == n.id,
                Activity.created_at >= today,
                Activity.created_at < tomorrow
            )
            .scalar() or 0
        )
        
        # تعداد فعالیت دیروز (برای داغ‌ترین)
        yesterday_count = (
            db.query(func.count(Activity.id))
            .join(User, User.id == Activity.user_id)
            .filter(
                User.neighborhood_id == n.id,
                Activity.created_at >= yesterday,
                Activity.created_at < today
            )
            .scalar() or 0
        )
        
        # فعالیت شبانه (22 تا 6)
        night_count = (
            db.query(func.count(Activity.id))
            .join(User, User.id == Activity.user_id)
            .filter(
                User.neighborhood_id == n.id,
                Activity.created_at >= today,
                Activity.created_at < tomorrow,
                func.extract('hour', Activity.created_at).in_([22, 23, 0, 1, 2, 3, 4, 5])
            )
            .scalar() or 0
        )
        
        # تعداد کاربران فعال امروز (برای رقابتی‌ترین)
        active_users = (
            db.query(func.count(func.distinct(User.id)))
            .join(Activity, Activity.user_id == User.id)
            .filter(
                User.neighborhood_id == n.id,
                Activity.created_at >= today,
                Activity.created_at < tomorrow
            )
            .scalar() or 0
        )
        
        metrics[n.id] = {
            "activity_count": activity_count,
            "yesterday_count": yesterday_count,
            "night_count": night_count,
            "active_users": active_users,
            "growth": activity_count - yesterday_count,
        }
    
    # ==== خونین‌ترین = بیشترین فعالیت ====
    if metrics:
        bloodiest_id = max(metrics, key=lambda k: metrics[k]["activity_count"])
        if metrics[bloodiest_id]["activity_count"] > 0:
            db.add(DailyNeighborhoodBadge(
                neighborhood_id=bloodiest_id,
                badge_type=DailyBadgeType.BLOODIEST,
                date=today,
                metric_value=metrics[bloodiest_id]["activity_count"]
            ))
        
        # ==== متروک‌ترین = کمترین فعالیت ====
        abandoned_id = min(metrics, key=lambda k: metrics[k]["activity_count"])
        db.add(DailyNeighborhoodBadge(
            neighborhood_id=abandoned_id,
            badge_type=DailyBadgeType.MOST_ABANDONED,
            date=today,
            metric_value=metrics[abandoned_id]["activity_count"]
        ))
        
        # ==== داغ‌ترین = بیشترین رشد ====
        hottest_id = max(metrics, key=lambda k: metrics[k]["growth"])
        if metrics[hottest_id]["growth"] > 0:
            db.add(DailyNeighborhoodBadge(
                neighborhood_id=hottest_id,
                badge_type=DailyBadgeType.HOTTEST,
                date=today,
                metric_value=metrics[hottest_id]["growth"]
            ))
        
        # ==== شب‌زنده‌دارترین ====
        night_id = max(metrics, key=lambda k: metrics[k]["night_count"])
        if metrics[night_id]["night_count"] > 0:
            db.add(DailyNeighborhoodBadge(
                neighborhood_id=night_id,
                badge_type=DailyBadgeType.NIGHT_OWL,
                date=today,
                metric_value=metrics[night_id]["night_count"]
            ))
        
        # ==== رقابتی‌ترین = بیشترین کاربر فعال ====
        competitive_id = max(metrics, key=lambda k: metrics[k]["active_users"])
        if metrics[competitive_id]["active_users"] > 0:
            db.add(DailyNeighborhoodBadge(
                neighborhood_id=competitive_id,
                badge_type=DailyBadgeType.MOST_COMPETITIVE,
                date=today,
                metric_value=metrics[competitive_id]["active_users"]
            ))
    
    db.commit()


def get_neighborhood_badges(db: Session, neighborhood_id: int):
    """نشان‌های فعال محله"""
    badges = (
        db.query(NeighborhoodBadge)
        .filter(
            NeighborhoodBadge.neighborhood_id == neighborhood_id,
            NeighborhoodBadge.is_active == True
        )
        .all()
    )
    return [
        {
            "id": b.id,
            "badge_type": b.badge_type,
            "user_id": b.user_id,
            "username": b.user.username,
            "display_name": b.user.display_name or b.user.username,
            "score_at_earn": b.score_at_earn,
            "period_start": b.period_start,
            "period_end": b.period_end,
        }
        for b in badges
    ]


def get_daily_badges(db: Session, neighborhood_id: int):
    """نشان‌های روزانه امروز محله"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    badges = (
        db.query(DailyNeighborhoodBadge)
        .filter(
            DailyNeighborhoodBadge.neighborhood_id == neighborhood_id,
            DailyNeighborhoodBadge.date >= today,
            DailyNeighborhoodBadge.date < tomorrow
        )
        .all()
    )
    return [
        {
            "id": b.id,
            "badge_type": b.badge_type,
            "metric_value": b.metric_value,
            "date": b.date,
        }
        for b in badges
    ]


def get_my_neighborhood_info(db: Session, user: User):
    """اطلاعات کامل محله کاربر"""
    if not user.neighborhood_id:
        return None
    
    n = db.query(Neighborhood).filter(Neighborhood.id == user.neighborhood_id).first()
    if not n:
        return None
    
    mayor = get_mayor(db, n.id)
    top_users = get_top_users(db, n.id, limit=10)
    badges = get_neighborhood_badges(db, n.id)
    daily_badges = get_daily_badges(db, n.id)
    my_rank = get_user_rank_in_neighborhood(db, user.id, n.id)
    rank_in_city = get_neighborhood_rank_in_city(db, n.id, n.city_id) if n.city_id else 0
    category = calculate_neighborhood_category(db, n.id)
    
    user_count = (
        db.query(func.count(User.id))
        .filter(User.neighborhood_id == n.id, User.is_active == True)
        .scalar() or 0
    )
    
    return {
        "id": n.id,
        "name": n.name,
        "city_id": n.city_id,
        "city_name": n.city.name if n.city else None,
        "total_score": sum(u["total_score"] for u in top_users),  # یا کوئری جداگانه
        "user_count": user_count,
        "rank_in_city": rank_in_city,
        "category": category,
        "mayor": {
            "id": mayor.id,
            "username": mayor.username,
            "display_name": mayor.display_name or mayor.username,
            "total_score": mayor.total_score,
            "rank": 1,
        } if mayor else None,
        "top_users": top_users,
        "badges": badges,
        "daily_badges": daily_badges,
        "my_rank": my_rank,
    }