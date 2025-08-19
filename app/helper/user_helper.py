from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import secrets
import string

from app.models import user as user_model
from app.models import relationship_type as relationship_type_model # RelationshipType 모델 임포트
from app.schemas import user_schema

def create_user(db: Session, user: user_schema.UserCreate):
    # 모든 필수 필드를 포함하여 사용자 생성
    db_user = user_model.User(
        username=user.username, 
        email=user.email, 
        hashed_password=user.password,  # password 필드를 hashed_password로 매핑
        role=user.role,  # 역할 필드 추가
        phone_number=user.phone_number,  # 전화번호 필드 추가
        full_name=user.username  # full_name을 username으로 설정 (기본값)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def get_user_by_email(db : Session, email : str) :
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def get_user_by_username(db : Session, username : str) :
    return db.query(user_model.User).filter(user_model.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[user_model.UserRole] = None):
    query = db.query(user_model.User)
    if role:
        query = query.filter(user_model.User.role == role)
    return query.offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: user_schema.UserUpdate):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "role": # role 필드 업데이트 시 Enum 값으로 변환
                setattr(db_user, key, user_model.UserRole(value))
            else:
                setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_guardians_for_senior(db: Session, senior_id: int) -> List[Dict[str, Any]]:
    # senior_id에 해당하는 사용자가 senior 역할인지 확인
    senior_user = db.query(user_model.User).filter(user_model.User.id == senior_id, user_model.User.role == user_model.UserRole.senior).first()
    if not senior_user:
        return []

    # 해당 senior_id와 연결된 보호자 정보와 관계 유형을 조인하여 가져옴
    guardians_info = db.query(
        user_model.User, 
        user_model.FamilyRelationship, 
        relationship_type_model.RelationshipType
    ).join(
        user_model.FamilyRelationship, user_model.User.id == user_model.FamilyRelationship.guardian_id
    ).join(
        relationship_type_model.RelationshipType, user_model.FamilyRelationship.relationship_type_id == relationship_type_model.RelationshipType.id
    ).filter(
        user_model.FamilyRelationship.senior_id == senior_id
    ).options(joinedload(user_model.User.seniors)).all() # seniors 관계를 미리 로드

    result = []
    for guardian_user, family_rel, rel_type in guardians_info:
        result.append({
            "id": guardian_user.id,
            "username": guardian_user.username,
            "email": guardian_user.email,
            "phone_number": guardian_user.phone_number, # 전화번호 포함
            "relationship_display_name": rel_type.display_name_ko # 관계 표시명 포함
        })
    return result

def get_seniors_by_guardian_id(db: Session, guardian_id: int) -> List[Dict[str, Any]]:
    # guardian_id에 해당하는 사용자가 guardian 역할인지 확인
    guardian_user = db.query(user_model.User).filter(user_model.User.id == guardian_id, user_model.User.role == user_model.UserRole.guardian).first()
    if not guardian_user:
        return []

    # 해당 guardian_id와 연결된 senior 정보와 관계 유형을 조인하여 가져옴
    seniors_info = db.query(
        user_model.User, 
        user_model.FamilyRelationship, 
        relationship_type_model.RelationshipType
    ).join(
        user_model.FamilyRelationship, user_model.User.id == user_model.FamilyRelationship.senior_id
    ).join(
        relationship_type_model.RelationshipType, user_model.FamilyRelationship.relationship_type_id == relationship_type_model.RelationshipType.id
    ).filter(
        user_model.FamilyRelationship.guardian_id == guardian_id
    ).options(joinedload(user_model.User.seniors)).all() # seniors 관계를 미리 로드

    result = []
    for senior_user, family_rel, rel_type in seniors_info:
        result.append({
            "id": senior_user.id,
            "username": senior_user.username,
            "email": senior_user.email,
            "phone_number": senior_user.phone_number, # 전화번호 포함
            "relationship_display_name": rel_type.display_name_ko # 관계 표시명 포함
        })
    return result

def create_family_relationship(db: Session, relationship: user_schema.FamilyRelationshipCreate):
    db_relationship = user_model.FamilyRelationship(
        senior_id=relationship.senior_id,
        guardian_id=relationship.guardian_id,
        relationship_type_id=relationship.relationship_type_id
    )
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship

# 초대코드 관련 헬퍼 함수들
def generate_invitation_code() -> str:
    """8자리 랜덤 초대코드 생성"""
    # 숫자와 대문자만 사용 (0, O, 1, I 등 혼동 문자 제외)
    characters = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(8))

def create_invitation_code(db: Session, senior_user_id: int, expires_in_hours: int = 24):
    """초대코드 생성 및 저장"""
    # 기존에 pending 상태인 초대코드가 있다면 만료 처리
    existing_codes = db.query(user_model.InvitationCode).filter(
        user_model.InvitationCode.senior_user_id == senior_user_id,
        user_model.InvitationCode.status == user_model.InvitationStatus.pending
    ).all()
    
    for code in existing_codes:
        code.status = user_model.InvitationStatus.expired
        db.add(code)
    
    # 새 초대코드 생성
    code = generate_invitation_code()
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    # 중복 코드가 없을 때까지 생성
    while db.query(user_model.InvitationCode).filter(user_model.InvitationCode.code == code).first():
        code = generate_invitation_code()
    
    invitation = user_model.InvitationCode(
        code=code,
        senior_user_id=senior_user_id,
        expires_at=expires_at
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return invitation

def get_invitation_code_by_code(db: Session, code: str):
    """초대코드로 초대 정보 조회"""
    return db.query(user_model.InvitationCode).filter(
        user_model.InvitationCode.code == code
    ).first()

def accept_invitation_code(db: Session, code: str, guardian_user_id: int):
    """초대코드 수락 및 가족 관계 생성"""
    invitation = get_invitation_code_by_code(db, code)
    if not invitation:
        return None, "초대코드를 찾을 수 없습니다."
    
    if invitation.status != user_model.InvitationStatus.pending:
        return None, "이미 사용되었거나 만료된 초대코드입니다."
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = user_model.InvitationStatus.expired
        db.add(invitation)
        db.commit()
        return None, "만료된 초대코드입니다."
    
    # 시니어와 보호자 역할 확인
    senior_user = get_user(db, invitation.senior_user_id)
    guardian_user = get_user(db, guardian_user_id)
    
    if not senior_user or not guardian_user:
        return None, "사용자를 찾을 수 없습니다."
    
    if senior_user.role != user_model.UserRole.senior:
        return None, "초대코드 생성자는 시니어 역할이어야 합니다."
    
    if guardian_user.role != user_model.UserRole.guardian:
        return None, "연결하려는 사용자는 보호자 역할이어야 합니다."
    
    # 이미 연결된 관계인지 확인
    existing_relationship = db.query(user_model.FamilyRelationship).filter(
        user_model.FamilyRelationship.senior_id == invitation.senior_user_id,
        user_model.FamilyRelationship.guardian_id == guardian_user_id
    ).first()
    
    if existing_relationship:
        return None, "이미 연결된 가족 관계입니다."
    
    # 초대코드 상태 업데이트
    invitation.status = user_model.InvitationStatus.accepted
    invitation.guardian_user_id = guardian_user_id
    invitation.accepted_at = datetime.utcnow()
    db.add(invitation)
    
    # 가족 관계 생성 (기본 관계 타입: 부모-자녀)
    default_relationship_type = db.query(relationship_type_model.RelationshipType).filter(
        relationship_type_model.RelationshipType.name == "부모-자녀"
    ).first()
    
    if not default_relationship_type:
        # 기본 관계 타입이 없으면 생성
        default_relationship_type = relationship_type_model.RelationshipType(
            name="부모-자녀",
            description="부모와 자녀 간의 관계"
        )
        db.add(default_relationship_type)
        db.commit()
        db.refresh(default_relationship_type)
    
    family_relationship = user_model.FamilyRelationship(
        senior_id=invitation.senior_user_id,
        guardian_id=guardian_user_id,
        relationship_type_id=default_relationship_type.id
    )
    db.add(family_relationship)
    
    db.commit()
    db.refresh(family_relationship)
    
    return family_relationship, "가족 연결이 완료되었습니다."

def get_user_family_members(db: Session, user_id: int):
    """사용자의 가족 구성원 조회"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    if user.role == user_model.UserRole.senior:
        # 시니어인 경우: 연결된 보호자들
        guardians = get_guardians_for_senior(db, user_id)
        return {
            "senior": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": "senior"
            },
            "guardians": guardians,
            "seniors": []
        }
    elif user.role == user_model.UserRole.guardian:
        # 보호자인 경우: 돌보는 시니어들
        seniors = get_seniors_by_guardian_id(db, user_id)
        return {
            "senior": None,
            "guardians": [],
            "seniors": seniors
        }
    
    return None

def get_user_invitations(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """사용자가 생성한 초대코드 목록 조회"""
    invitations = db.query(user_model.InvitationCode).filter(
        user_model.InvitationCode.senior_user_id == user_id
    ).order_by(user_model.InvitationCode.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(user_model.InvitationCode).filter(
        user_model.InvitationCode.senior_user_id == user_id
    ).count()
    
    return invitations, total

def cleanup_expired_invitations(db: Session):
    """만료된 초대코드 정리"""
    expired_invitations = db.query(user_model.InvitationCode).filter(
        user_model.InvitationCode.expires_at < datetime.utcnow(),
        user_model.InvitationCode.status == user_model.InvitationStatus.pending
    ).all()
    
    for invitation in expired_invitations:
        invitation.status = user_model.InvitationStatus.expired
        db.add(invitation)
    
    db.commit()
    return len(expired_invitations)