from sqlalchemy.orm import Session
from app.models.badge import Badge, UserBadge, BadgeType
from app.models.user import User
from app.models.activity import Activity


def get_badge_by_type(db: Session, badge_type: BadgeType):
    return db.query(Badge).filter(Badge.badge_type == badge_type).first()


def user_has_badge(db: Session, user_id: int, badge_id: int) -> bool:
    """بررسی اینکه کاربر قبلاً این نشان را گرفته یا نه"""
    return db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first() is not None


def award_badge(db: Session, user: User, badge: Badge) -> UserBadge:
    """اهدا نشان به کاربر"""
    user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
    db.add(user_badge)
    db.commit()
    db.refresh(user_badge)
    return user_badge


def check_and_award_badges(db: Session, user: User, activity: Activity):
    """بررسی شرایط اهدای نشان پس از ثبت فعالیت"""
    awarded_badges = []
    
    # 1. اولین فعالیت
    first_activity_badge = get_badge_by_type(db, BadgeType.FIRST_ACTIVITY)
    if first_activity_badge and not user_has_badge(db, user.id, first_activity_badge.id):
        awarded_badges.append(award_badge(db, user, first_activity_badge))
    
    # 2. مسافت 10 کیلومتر (مجموع)
    total_distance = db.query(Activity).filter(
        Activity.user_id == user.id
    ).with_entities(
        __import__('sqlalchemy').func.sum(Activity.distance_km)
    ).scalar() or 0
    
    if total_distance >= 10:
        badge_10km = get_badge_by_type(db, BadgeType.DISTANCE_10KM)
        if badge_10km and not user_has_badge(db, user.id, badge_10km.id):
            awarded_badges.append(award_badge(db, user, badge_10km))
    
    if total_distance >= 50:
        badge_50km = get_badge_by_type(db, BadgeType.DISTANCE_50KM)
        if badge_50km and not user_has_badge(db, user.id, badge_50km.id):
            awarded_badges.append(award_badge(db, user, badge_50km))
    
    return awarded_badges


def seed_badges(db: Session):
    """ساخت نشان‌های پیش‌فرض در دیتابیس"""
    default_badges = [
        {"name": "شروع سفر", "description": "اولین فعالیت خود را ثبت کردید", "badge_type": BadgeType.FIRST_ACTIVITY},
        {"name": "اولین قدم", "description": "اولین پیاده‌روی خود را انجام دادید", "badge_type": BadgeType.FIRST_WALK},
        {"name": "ده کیلومتری", "description": "مجموعاً 10 کیلومتر فعالیت کردید", "badge_type": BadgeType.DISTANCE_10KM},
        {"name": "پنجاه کیلومتری", "description": "مجموعاً 50 کیلومتر فعالیت کردید", "badge_type": BadgeType.DISTANCE_50KM},
        {"name": "استقامت", "description": "7 روز متوالی فعالیت کردید", "badge_type": BadgeType.STREAK_7DAYS},
        {"name": "سحرخیز", "description": "قبل از ساعت 7 صبح فعالیت کردید", "badge_type": BadgeType.EARLY_BIRD},
        {"name": "شب‌زنده‌دار", "description": "بعد از ساعت 22 فعالیت کردید", "badge_type": BadgeType.NIGHT_OWL},
    ]
    
    for badge_data in default_badges:
        existing = db.query(Badge).filter(Badge.badge_type == badge_data["badge_type"]).first()
        if not existing:
            db.add(Badge(**badge_data))
    
    db.commit()