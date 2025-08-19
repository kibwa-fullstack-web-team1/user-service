import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.invitation import Invitation
from app.models.user import User, UserRole, FamilyRelationship
from app.models.relationship_type import RelationshipType

def generate_invitation_code() -> str:
    """8자리 랜덤 초대코드 생성"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_invitation_code(
    db: Session, 
    inviter_id: int, 
    invitee_email: str = None,
    relationship_type_id: int = None,
    expires_hours: int = 24
) -> Invitation:
    """초대코드 생성 및 저장"""
    
    # 시니어 사용자인지 확인
    senior_user = db.query(User).filter(User.id == inviter_id).first()
    if not senior_user or senior_user.role != UserRole.senior:
        raise ValueError("시니어 사용자만 초대코드를 생성할 수 있습니다.")
    
    # 기존에 만료되지 않은 초대코드가 있다면 만료 처리
    existing_invitations = db.query(Invitation).filter(
        Invitation.inviter_id == inviter_id,
        Invitation.is_used == False,
        Invitation.expires_at > datetime.utcnow()
    ).all()
    
    for inv in existing_invitations:
        inv.is_used = True
        inv.used_at = datetime.utcnow()
    
    # 새로운 초대코드 생성
    while True:
        code = generate_invitation_code()
        # 중복 코드 확인
        if not db.query(Invitation).filter(Invitation.code == code).first():
            break
    
    # 초대코드 저장
    invitation = Invitation(
        code=code,
        inviter_id=inviter_id,
        invitee_email=invitee_email,
        relationship_type_id=relationship_type_id,
        is_used=False,
        expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
        is_group_code=False,  # 개별 초대코드임을 명시
        max_guardians=1,  # 개별 초대코드는 최대 1명
        current_guardians=0,
        is_active=True
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return invitation

def create_group_invitation_code(
    db: Session, 
    inviter_id: int, 
    max_guardians: int = 10,
    relationship_type_id: int = None,
    expires_in_days: int = 30
) -> Invitation:
    """그룹 초대코드 생성 및 저장 (여러 보호자 연결 가능)"""
    
    # 시니어 사용자인지 확인
    inviter_user = db.query(User).filter(User.id == inviter_id).first()
    if not inviter_user or inviter_user.role != UserRole.senior:
        raise ValueError("시니어 사용자만 그룹 초대코드를 생성할 수 있습니다.")
    
    # 기존에 활성화된 그룹 초대코드가 있다면 비활성화
    existing_group_invitations = db.query(Invitation).filter(
        Invitation.inviter_id == inviter_id,
        Invitation.is_group_code == True,
        Invitation.is_active == True
    ).all()
    
    for inv in existing_group_invitations:
        inv.is_active = False
    
    # 새로운 그룹 초대코드 생성
    while True:
        code = generate_invitation_code()
        # 중복 코드 확인
        if not db.query(Invitation).filter(Invitation.code == code).first():
            break
    
    # 그룹 초대코드 저장
    invitation = Invitation(
        code=code,
        inviter_id=inviter_id,
        invitee_email=None,  # 그룹 초대코드는 이메일 불필요
        relationship_type_id=relationship_type_id,
        is_used=False,  # 그룹 초대코드는 is_used 대신 is_active 사용
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        used_at=None,  # 그룹 초대코드는 used_at 불필요
        is_group_code=True,  # 그룹 초대코드임을 명시
        max_guardians=max_guardians,
        current_guardians=0,
        is_active=True
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return invitation

def get_invitation_code_by_code(db: Session, code: str) -> Invitation:
    """코드로 초대 정보 조회"""
    return db.query(Invitation).filter(Invitation.code == code).first()

def accept_invitation_code(
    db: Session, 
    code: str, 
    guardian_user_id: int,
    relationship_type_id: int = None
) -> FamilyRelationship:
    """초대코드로 가족 연결 수락"""
    
    # 보호자 사용자인지 확인
    guardian_user = db.query(User).filter(User.id == guardian_user_id).first()
    if not guardian_user or guardian_user.role != UserRole.guardian:
        raise ValueError("보호자 사용자만 초대코드를 수락할 수 있습니다.")
    
    # 초대코드 조회 및 검증
    invitation = get_invitation_code_by_code(db, code)
    if not invitation:
        raise ValueError("유효하지 않은 초대코드입니다.")
    
    if invitation.is_used:
        raise ValueError("이미 사용된 초대코드입니다.")
    
    if invitation.expires_at < datetime.utcnow():
        raise ValueError("만료된 초대코드입니다.")
    
    # 시니어와 보호자가 이미 연결되어 있는지 확인
    existing_relationship = db.query(FamilyRelationship).filter(
        FamilyRelationship.senior_id == invitation.inviter_id,
        FamilyRelationship.guardian_id == guardian_user_id
    ).first()
    
    if existing_relationship:
        raise ValueError("이미 연결된 가족 관계입니다.")
    
    # 가족 관계 생성
    family_relationship = FamilyRelationship(
        senior_id=invitation.inviter_id,
        guardian_id=guardian_user_id,
        relationship_type_id=relationship_type_id or invitation.relationship_type_id
    )
    
    db.add(family_relationship)
    
    # 초대코드 사용 처리
    invitation.is_used = True
    invitation.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(family_relationship)
    
    return family_relationship

def get_user_family_members(db: Session, user_id: int) -> dict:
    """사용자의 가족 구성원 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"seniors": [], "guardians": []}
    
    if user.role == UserRole.senior:
        # 시니어인 경우: 자신을 돌보는 보호자들
        guardians = db.query(FamilyRelationship).filter(
            FamilyRelationship.senior_id == user_id
        ).all()
        
        guardian_users = []
        for rel in guardians:
            guardian = db.query(User).filter(User.id == rel.guardian_id).first()
            if guardian:
                guardian_users.append({
                    "id": guardian.id,
                    "username": guardian.username,
                    "full_name": guardian.full_name,
                    "relationship_type": rel.relationship_type.display_name_ko if rel.relationship_type else None
                })
        
        return {"seniors": [], "guardians": guardian_users}
    
    else:
        # 보호자인 경우: 자신이 돌보는 시니어들
        seniors = db.query(FamilyRelationship).filter(
            FamilyRelationship.guardian_id == user_id
        ).all()
        
        senior_users = []
        for rel in seniors:
            senior = db.query(User).filter(User.id == rel.senior_id).first()
            if senior:
                senior_users.append({
                    "id": senior.id,
                    "username": senior.username,
                    "full_name": senior.full_name,
                    "relationship_type": rel.relationship_type.display_name_ko if rel.relationship_type else None
                })
        
        return {"seniors": senior_users, "guardians": []}

def get_user_invitations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list:
    """사용자가 생성한 초대코드 목록 조회"""
    invitations = db.query(Invitation).filter(
        Invitation.inviter_id == user_id
    ).order_by(Invitation.created_at.desc()).offset(skip).limit(limit).all()
    
    return invitations

def cleanup_expired_invitations(db: Session) -> int:
    """만료된 초대코드 정리"""
    expired_count = db.query(Invitation).filter(
        Invitation.expires_at < datetime.utcnow(),
        Invitation.is_used == False
    ).count()
    
    db.query(Invitation).filter(
        Invitation.expires_at < datetime.utcnow(),
        Invitation.is_used == False
    ).update({"is_used": True, "used_at": datetime.utcnow()})
    
    db.commit()
    return expired_count
