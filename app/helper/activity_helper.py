from sqlalchemy.orm import Session
from typing import List

from app import models, schemas

def create_activity_type(db: Session, activity_type: schemas.ActivityTypeCreate):
    db_activity_type = models.ActivityType(**activity_type.model_dump())
    db.add(db_activity_type)
    db.commit()
    db.refresh(db_activity_type)
    return db_activity_type

def read_activity_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ActivityType).offset(skip).limit(limit).all()

def create_activity_log(db: Session, activity_log: schemas.ActivityLogCreate):
    # 사용자 존재 여부 확인
    db_user = db.query(models.User).filter(models.User.id == activity_log.user_id).first()
    if db_user is None:
        return None, "User not found"
    
    # 활동 유형 존재 여부 확인
    db_activity_type = db.query(models.ActivityType).filter(models.ActivityType.id == activity_log.activity_type_id).first()
    if db_activity_type is None:
        return None, "ActivityType not found"

    db_activity_log = models.ActivityLog(**activity_log.model_dump())
    db.add(db_activity_log)
    db.commit()
    db.refresh(db_activity_log)
    return db_activity_log, None

def read_activity_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # 사용자 존재 여부 확인
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None, "User not found"
        
    activity_logs = db.query(models.ActivityLog).filter(models.ActivityLog.user_id == user_id).offset(skip).limit(limit).all()
    return activity_logs, None
