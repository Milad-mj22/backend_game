from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Clan(Base):
    __tablename__ = "clans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # سازنده کلن
    
    # امتیاز کل کلن
    total_score = Column(Integer, default=0)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ارتباط‌ها
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("ClanMember", back_populates="clan", cascade="all, delete-orphan")


class ClanMember(Base):
    __tablename__ = "clan_members"

    id = Column(Integer, primary_key=True, index=True)
    clan_id = Column(Integer, ForeignKey("clans.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # نقش در کلن
    role = Column(String, default="member")  # owner, admin, member
    
    # امتیاز اکتسابی کاربر در کلن (طبق سند: خروج عضو نباید فعالیت‌هایش را حذف کند)
    contribution_score = Column(Integer, default=0)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    clan = relationship("Clan", back_populates="members")
    user = relationship("User")