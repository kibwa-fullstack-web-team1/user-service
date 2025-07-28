from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any

from app.models import user as user_model
from app.models import relationship_type as relationship_type_model # RelationshipType 모델 임포트
from app.schemas import user_schema

def create_user(db: Session, user: user_schema.UserCreate):
    db_user = user_model.User(username=user.username, email=user.email, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def get_user_by_email(db : Session, email : str) :
    return db.query(user_model.User).filter(user_model.User.email == email).first()

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
