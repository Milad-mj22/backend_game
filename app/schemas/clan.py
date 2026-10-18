from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ClanBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None


class ClanCreate(ClanBase):
    pass


class ClanMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str
    contribution_score: int
    joined_at: datetime
    username: str
    display_name: str

    class Config:
        from_attributes = True


class ClanResponse(ClanBase):
    id: int
    owner_id: int
    total_score: int
    is_active: bool
    created_at: datetime
    member_count: int = 0

    class Config:
        from_attributes = True


class ClanDetailResponse(ClanResponse):
    members: List[ClanMemberResponse] = []


class GroupActivityRequest(BaseModel):
    activity_type: str
    distance_km: float
    duration_minutes: int
    participants: List[int]