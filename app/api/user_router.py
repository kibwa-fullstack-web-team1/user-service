from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user import UserRole
from starlette.concurrency import run_in_threadpool # run_in_threadpool 임포트

from app.schemas import user_schema
from app.models import user as user_model
from app.utils.db import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

from app.helper import user_helper

@router.post("/", response_model=user_schema.User)
async def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return await run_in_threadpool(user_helper.create_user, db=db, user=user)

@router.get("/{user_id}", response_model=user_schema.User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await run_in_threadpool(user_helper.get_user, db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/", response_model=List[user_schema.User])
async def get_users(skip: int = 0, limit: int = 100, role: Optional[UserRole] = None, db: Session = Depends(get_db)):
    return await run_in_threadpool(user_helper.get_users, db=db, skip=skip, limit=limit, role=role)

@router.put("/{user_id}", response_model=user_schema.User)
async def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    db_user = await run_in_threadpool(user_helper.update_user, db=db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=user_schema.User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = await run_in_threadpool(user_helper.delete_user, db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.get("/guardian/{guardian_id}/seniors", response_model=List[user_schema.SeniorInfo])
async def get_seniors_for_guardian(guardian_id: int, db: Session = Depends(get_db)):
    seniors = await run_in_threadpool(user_helper.get_seniors_by_guardian_id, db=db, guardian_id=guardian_id)
    if not seniors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seniors not found for this guardian.")
    return seniors

@router.get("/{senior_id}/guardians", response_model=List[user_schema.GuardianInfo])
async def get_guardians_for_senior(senior_id: int, db: Session = Depends(get_db)):
    guardians = await run_in_threadpool(user_helper.get_guardians_for_senior, db=db, senior_id=senior_id)
    if not guardians:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardians not found for this senior")
    return guardians