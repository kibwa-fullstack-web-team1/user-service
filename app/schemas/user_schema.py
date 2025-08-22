from pydantic import BaseModel, ConfigDict, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, InvitationStatus # UserRole, InvitationStatus 임포트

class UserBase(BaseModel):
    username: str
    email: str
    phone_number: Optional[str] = None # 전화번호 필드 추가
    role: UserRole = UserRole.senior # 역할 필드 추가, 기본값 senior
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('사용자명은 2자 이상 50자 이하여야 합니다.')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('사용자명은 영문, 숫자, 언더스코어(_), 하이픈(-)만 사용 가능합니다.')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('유효한 이메일 주소를 입력해주세요.')
        return v.lower()
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # 전화번호 형식 검증 (한국 전화번호)
            import re
            phone_pattern = re.compile(r'^01[0-9]-\d{3,4}-\d{4}$')
            if not phone_pattern.match(v):
                raise ValueError('전화번호 형식이 올바르지 않습니다. (예: 010-1234-5678)')
        return v

class UserCreate(UserBase):
    password: str  # 평문 비밀번호
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        if not any(c.isupper() for c in v):
            raise ValueError('비밀번호는 대문자를 포함해야 합니다.')
        if not any(c.islower() for c in v):
            raise ValueError('비밀번호는 소문자를 포함해야 합니다.')
        if not any(c.isdigit() for c in v):
            raise ValueError('비밀번호는 숫자를 포함해야 합니다.')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None # 전화번호 필드 추가
    password: Optional[str] = None  # 비밀번호 변경용
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
    user_role: str  # 사용자 역할 추가
    username: str # <--- ADDED

class RegisterResponse(BaseModel):
    message: str = "회원가입이 완료되었습니다."
    access_token: str
    token_type: str = "bearer"
    user_role: str
    username: str

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

# 초대코드 관련 스키마
class InvitationCodeCreate(BaseModel):
    senior_user_id: int
    expires_in_hours: int = 24

class InvitationCodeResponse(BaseModel):
    id: int
    code: str
    senior_user_id: int
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class InvitationCodeDisplay(BaseModel):
    invitation_code: str
    expires_at: datetime
    qr_code_url: str

class FamilyConnectRequest(BaseModel):
    invitation_code: str
    guardian_user_id: int

class FamilyConnectResponse(BaseModel):
    message: str
    senior_name: str
    relationship_id: int

class InvitationCodeStatus(BaseModel):
    code: str
    senior_name: str
    status: InvitationStatus
    expires_at: datetime

class FamilyMembersResponse(BaseModel):
    senior: Optional[SeniorInfo] = None
    guardians: List[GuardianInfo] = []
    seniors: List[SeniorInfo] = []

class InvitationCodeListResponse(BaseModel):
    invitations: List[InvitationCodeResponse]
    total: int