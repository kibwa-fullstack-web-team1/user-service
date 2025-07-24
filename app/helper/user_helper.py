from sqlalchemy.orm import Session
from typing import List
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError # OperationalError 임포트

from app.models import user as user_model
from app.schemas import user_schema

# OperationalError 발생 시 재시도하도록 설정
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def create_user(db: Session, user: user_schema.UserCreate):
    db_user = user_model.User(username=user.username, email=user.email, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def get_user_by_email(db : Session, email : str) :
    return db.query(user_model.User).filter(user_model.User.email == email).first()

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_model.User).offset(skip).limit(limit).all()

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
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

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def delete_user(db: Session, user_id: int):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def get_guardians_of_senior(db: Session, senior_id: int) -> List[user_model.User]:
    return (
        db.query(user_model.User)
        .join(user_model.FamilyRelationship, user_model.User.id == user_model.FamilyRelationship.guardian_id)
        .filter(user_model.FamilyRelationship.senior_id == senior_id)
        .all()
    )

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def get_seniors_of_guardian(db: Session, guardian_id: int) -> List[user_model.User]:
    return (
        db.query(user_model.User)
        .join(user_model.FamilyRelationship, user_model.User.id == user_model.FamilyRelationship.senior_id)
        .filter(user_model.FamilyRelationship.guardian_id == guardian_id)
        .all()
    )