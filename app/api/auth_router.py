from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin, Token, User as UserSchema
from app.models import user as user_model
from app.utils.db import get_db
from app.utils import security
from app.helper import user_helper
from datetime import timedelta

router = APIRouter(prefix = "/auth", tags = ["Auth"])

@router.post("/register", response_model = UserSchema)
def register(user : UserCreate, db : Session = Depends(get_db)) :
    # 비밀번호 해시 적용
    user.hashed_password = security.hash_password(user.hashed_password)
    db_user = user_helper.create_user(db = db, user = user)
    return UserSchema.model_validate(db_user, from_attributes = True)

@router.post("/login", response_model = Token)
def login(login_data : UserLogin, db : Session = Depends(get_db)) :
    user = user_helper.get_user_by_email(db = db, email = login_data.email)
    if not user or not security.verify_password(login_data.password, user.hashed_password) :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "이메일 또는 비밀번호가 올바르지 않습니다.")
    access_token = security.create_access_token({"sub" : str(user.id)})
    return {"access_token" : access_token, "token_type" : "bearer"}

@router.post("/logout")
def logout() :
    # JWT 방식에서는 클라이언트에서 토큰 삭제만 하면 됨
    return {"msg" : "로그아웃되었습니다. 토큰을 삭제하세요."}