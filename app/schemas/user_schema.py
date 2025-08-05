from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole # UserRole 임포트

class UserBase(BaseModel):
    username: str
    email: str
    phone_number: Optional[str] = None # 전화번호 필드 추가
    hashed_password: str # 추가
    role: UserRole = UserRole.senior # 역할 필드 추가, 기본값 senior

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None # 전화번호 필드 추가
    hashed_password: Optional[str] = None
    role: Optional[UserRole] = None # 역할 필드 추가

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel) :
    email : str
    password : str

class Token(BaseModel) :
    access_token : str
    token_type : str = "bearer"

class GuardianInfo(BaseModel):
    id: int
    username: str
    email: str
    phone_number: Optional[str] = None
    relationship_display_name: str

    model_config = ConfigDict(from_attributes=True)

class SeniorInfo(BaseModel):
    id: int
    username: str
    email: str
    phone_number: Optional[str] = None
    relationship_display_name: str

    model_config = ConfigDict(from_attributes=True)

class FamilyRelationshipCreate(BaseModel):
    senior_id: int
    guardian_id: int
    relationship_type_id: int

class FamilyRelationshipResponse(BaseModel):
    id: int
    senior_id: int
    guardian_id: int
    relationship_type_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)