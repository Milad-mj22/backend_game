from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.clan import Clan, ClanMember
from app.models.user import User
from app.models.activity import ActivityType
from app.schemas.clan import ClanCreate


def get_clan_by_id(db: Session, clan_id: int):
    return db.query(Clan).filter(Clan.id == clan_id).first()


def get_clan_by_name(db: Session, name: str):
    return db.query(Clan).filter(Clan.name == name).first()


def get_user_clan(db: Session, user_id: int):
    membership = db.query(ClanMember).filter(ClanMember.user_id == user_id).first()
    if membership:
        return membership.clan
    return None


def get_user_membership(db: Session, user_id: int, clan_id: int):
    return db.query(ClanMember).filter(
        ClanMember.user_id == user_id,
        ClanMember.clan_id == clan_id
    ).first()


def get_all_clans(db: Session):
    return (
        db.query(Clan)
        .filter(Clan.is_active == True)
        .order_by(Clan.total_score.desc())
        .all()
    )


def create_clan(db: Session, owner: User, clan: ClanCreate):
    if get_user_clan(db, owner.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شما قبلاً در یک کلن عضو هستید"
        )
    
    if get_clan_by_name(db, clan.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نام کلن قبلاً استفاده شده است"
        )
    
    db_clan = Clan(
        name=clan.name,
        description=clan.description,
        owner_id=owner.id
    )
    db.add(db_clan)
    db.commit()
    db.refresh(db_clan)
    
    db_member = ClanMember(
        clan_id=db_clan.id,
        user_id=owner.id,
        role="owner"
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_clan)
    return db_clan


def join_clan(db: Session, user: User, clan_id: int):
    if get_user_clan(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شما قبلاً در یک کلن عضو هستید"
        )
    
    clan = get_clan_by_id(db, clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="کلن یافت نشد")
    
    db_member = ClanMember(clan_id=clan_id, user_id=user.id, role="member")
    db.add(db_member)
    db.commit()
    return clan


def leave_clan(db: Session, user: User):
    membership = get_user_clan(db, user.id)
    if not membership:
        raise HTTPException(status_code=400, detail="شما در هیچ کلنی عضو نیستید")
    
    if membership.owner_id == user.id:
        raise HTTPException(
            status_code=400,
            detail="شما سازنده این کلن هستید و نمی‌توانید آن را ترک کنید"
        )
    
    db_member = db.query(ClanMember).filter(
        ClanMember.user_id == user.id,
        ClanMember.clan_id == membership.id
    ).first()
    db.delete(db_member)
    db.commit()
    return True


def calculate_group_multiplier(member_count: int) -> float:
    """ضریب گروهی طبق سند"""
    if member_count < 2:
        return 0.0
    elif member_count == 2:
        return 1.0
    elif member_count == 3:
        return 1.2
    elif member_count == 4:
        return 1.4
    else:
        return 1.5


def register_group_activity(
    db: Session,
    clan: Clan,
    activity_type: str,
    distance_km: float,
    duration_minutes: int,
    participants: list[int]
):
    """ثبت فعالیت گروهی طبق سند"""
    if len(participants) < 2:
        raise HTTPException(
            status_code=400,
            detail="حداقل دو عضو برای ثبت فعالیت گروهی لازم است"
        )
    
    clan_member_ids = [m.user_id for m in clan.members]
    for p in participants:
        if p not in clan_member_ids:
            raise HTTPException(
                status_code=400,
                detail=f"کاربر {p} عضو این کلن نیست"
            )
    
    from app.services.activity_service import calculate_score
    
    base_score, _ = calculate_score(
        ActivityType(activity_type),
        distance_km,
        duration_minutes
    )
    
    multiplier = calculate_group_multiplier(len(participants))
    total_score = base_score * multiplier
    score_per_member = total_score / len(participants)
    
    for user_id in participants:
        membership = db.query(ClanMember).filter(
            ClanMember.clan_id == clan.id,
            ClanMember.user_id == user_id
        ).first()
        if membership:
            membership.contribution_score += int(score_per_member)
    
    clan.total_score += int(total_score)
    db.commit()
    db.refresh(clan)
    
    return {
        "clan_id": clan.id,
        "participants": participants,
        "multiplier": multiplier,
        "total_score": int(total_score),
        "score_per_member": int(score_per_member)
    }