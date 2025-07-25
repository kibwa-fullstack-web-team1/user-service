from sqlalchemy import Column, Integer, String, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.db import Base
import enum

class UserRole(enum.Enum):
    senior = "senior"
    guardian = "guardian"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=True) # 전화번호 필드 추가
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    role = Column(Enum(UserRole), default=UserRole.senior, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 노인 사용자의 경우: 자신을 등록한 보호자 목록
    guardians = relationship(
        "FamilyRelationship",
        foreign_keys="[FamilyRelationship.senior_id]",
        back_populates="senior",
        cascade="all, delete-orphan"
    )

    # 보호자 사용자의 경우: 자신이 돌보는 노인 목록
    seniors = relationship(
        "FamilyRelationship",
        foreign_keys="[FamilyRelationship.guardian_id]",
        back_populates="guardian",
        cascade="all, delete-orphan"
    )


class FamilyRelationship(Base):
    __tablename__ = "family_relationships"

    id = Column(Integer, primary_key=True, index=True)
    senior_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guardian_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    relationship_type = Column(String) # 예: "딸", "아들"

    created_at = Column(DateTime, server_default=func.now())

    senior = relationship("User", foreign_keys=[senior_id], back_populates="guardians")
    guardian = relationship("User", foreign_keys=[guardian_id], back_populates="seniors")
