from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import InvitationStatus

class InvitationCodeCreate(BaseModel):
    """초대코드 생성 요청"""
    invitee_email: Optional[EmailStr] = None
    relationship_type_id: Optional[int] = None
    is_group_code: bool = False  # 그룹 초대코드 여부

class GroupInvitationCodeCreate(BaseModel):
    """그룹 초대코드 생성 요청"""
    max_guardians: Optional[int] = 10  # 최대 보호자 수 (기본값 10명)
    relationship_type_id: Optional[int] = None
    expires_in_days: Optional[int] = 30  # 만료일 (기본값 30일)

class GroupInvitationCodeResponse(BaseModel):
    """그룹 초대코드 응답"""
    id: int
    code: str
    inviter_id: int
    max_guardians: int
    current_guardians: int  # 현재 연결된 보호자 수
    relationship_type_id: Optional[int] = None
    expires_at: datetime
    created_at: datetime
    is_active: bool  # 그룹 초대코드 활성화 상태
    is_group_code: bool = True  # 그룹 초대코드임을 명시
    
    class Config:
        from_attributes = True

class InvitationCodeResponse(BaseModel):
    """초대코드 응답"""
    id: int
    code: str
    inviter_id: int
    invitee_email: Optional[str] = None
    relationship_type_id: Optional[int] = None
    is_used: bool
    expires_at: datetime
    created_at: datetime
    is_group_code: bool = False  # 개별 초대코드임을 명시 (기본값)
    
    class Config:
        from_attributes = True

class InvitationCodeDisplay(BaseModel):
    """초대코드 표시용 (시니어에게 보여줄 정보)"""
    code: str
    expires_at: datetime
    created_at: datetime
    is_used: bool

class FamilyConnectRequest(BaseModel):
    """가족 연결 요청 (보호자가 초대코드 입력)"""
    code: str
    relationship_type_id: Optional[int] = None

class FamilyConnectResponse(BaseModel):
    """가족 연결 응답"""
    success: bool
    message: str
    family_relationship_id: Optional[int] = None

class InvitationCodeStatus(BaseModel):
    """초대코드 상태 확인 응답"""
    code: str
    is_valid: bool
    is_used: bool
    expires_at: datetime
    inviter_name: Optional[str] = None
    relationship_type: Optional[str] = None

class FamilyMembersResponse(BaseModel):
    """가족 구성원 조회 응답"""
    seniors: list = []  # 보호자 입장에서 돌보는 시니어들
    guardians: list = []  # 시니어 입장에서 보호자들

class InvitationCodeListResponse(BaseModel):
    """초대코드 목록 조회 응답"""
    invitations: list[InvitationCodeResponse]
    total_count: int
