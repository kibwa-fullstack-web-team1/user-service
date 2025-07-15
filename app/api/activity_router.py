from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.utils.db import get_db # get_db를 app.utils.db에서 임포트

router = APIRouter(
    prefix="/activity",
    tags=["Activities"],
)

# DB 세션을 가져오는 의존성 (기존 get_db 함수 정의 제거)

from app.helper import activity_helper

# 활동 유형(ActivityType) API
@router.post("/types/", response_model=schemas.ActivityType)
def create_activity_type(activity_type: schemas.ActivityTypeCreate, db: Session = Depends(get_db)):
    return activity_helper.create_activity_type(db=db, activity_type=activity_type)

@router.get("/types/", response_model=List[schemas.ActivityType])
def read_activity_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return activity_helper.read_activity_types(db=db, skip=skip, limit=limit)

# 활동 로그(ActivityLog) API
@router.post("/logs/", response_model=schemas.ActivityLog)
def create_activity_log(activity_log: schemas.ActivityLogCreate, db: Session = Depends(get_db)):
    db_activity_log, error_message = activity_helper.create_activity_log(db=db, activity_log=activity_log)
    if error_message:
        raise HTTPException(status_code=404, detail=error_message)
    return db_activity_log

@router.get("/logs/user/{user_id}", response_model=List[schemas.ActivityLogWithDetails])
def read_activity_logs_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activity_logs, error_message = activity_helper.read_activity_logs_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    if error_message:
        raise HTTPException(status_code=404, detail=error_message)
    return activity_logs
