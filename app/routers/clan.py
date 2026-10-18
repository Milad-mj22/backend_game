from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.clan import (
    ClanCreate, ClanResponse, ClanDetailResponse, GroupActivityRequest
)
from app.services import clan_service
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/clans",
    tags=["Clans"]
)


@router.post("/", response_model=ClanResponse, status_code=status.HTTP_201_CREATED)
def create_clan(
    clan: ClanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return clan_service.create_clan(db, current_user, clan)


@router.get("/", response_model=List[ClanResponse])
def list_clans(db: Session = Depends(get_db)):
    clans = clan_service.get_all_clans(db)
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "owner_id": c.owner_id,
            "total_score": c.total_score,
            "is_active": c.is_active,
            "created_at": c.created_at,
            "member_count": len(c.members),
        }
        for c in clans
    ]


@router.get("/me", response_model=ClanDetailResponse)
def get_my_clan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    clan = clan_service.get_user_clan(db, current_user.id)
    if not clan:
        raise HTTPException(status_code=404, detail="شما در هیچ کلنی عضو نیستید")
    
    members_data = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "role": m.role,
            "contribution_score": m.contribution_score,
            "joined_at": m.joined_at,
            "username": m.user.username,
            "display_name": m.user.display_name or m.user.username,
        }
        for m in clan.members
    ]
    
    return {
        "id": clan.id,
        "name": clan.name,
        "description": clan.description,
        "owner_id": clan.owner_id,
        "total_score": clan.total_score,
        "is_active": clan.is_active,
        "created_at": clan.created_at,
        "member_count": len(clan.members),
        "members": members_data,
    }


@router.get("/{clan_id}", response_model=ClanDetailResponse)
def get_clan_detail(clan_id: int, db: Session = Depends(get_db)):
    clan = clan_service.get_clan_by_id(db, clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="کلن یافت نشد")
    
    members_data = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "role": m.role,
            "contribution_score": m.contribution_score,
            "joined_at": m.joined_at,
            "username": m.user.username,
            "display_name": m.user.display_name or m.user.username,
        }
        for m in clan.members
    ]
    
    return {
        "id": clan.id,
        "name": clan.name,
        "description": clan.description,
        "owner_id": clan.owner_id,
        "total_score": clan.total_score,
        "is_active": clan.is_active,
        "created_at": clan.created_at,
        "member_count": len(clan.members),
        "members": members_data,
    }


@router.post("/{clan_id}/join", response_model=ClanResponse)
def join_clan(
    clan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    clan = clan_service.join_clan(db, current_user, clan_id)
    return {
        "id": clan.id,
        "name": clan.name,
        "description": clan.description,
        "owner_id": clan.owner_id,
        "total_score": clan.total_score,
        "is_active": clan.is_active,
        "created_at": clan.created_at,
        "member_count": len(clan.members),
    }


@router.post("/leave")
def leave_clan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    clan_service.leave_clan(db, current_user)
    return {"message": "با موفقیت از کلن خارج شدید"}


@router.post("/me/group-activity")
def register_group_activity(
    data: GroupActivityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    clan = clan_service.get_user_clan(db, current_user.id)
    if not clan:
        raise HTTPException(status_code=404, detail="شما در هیچ کلنی عضو نیستید")
    
    return clan_service.register_group_activity(
        db, clan,
        data.activity_type,
        data.distance_km,
        data.duration_minutes,
        data.participants
    )