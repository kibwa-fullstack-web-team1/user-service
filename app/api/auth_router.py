from fastapi import APIRouter, Depends, HTTPException, status, Request
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

@router.get("/verify")
async def verify_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """토큰 검증 및 사용자 정보 반환"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization 헤더 형식이 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    
    try:
        # JWT 토큰 디코딩
        payload = security.decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
        
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에서 사용자 ID를 추출할 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
        
        # 사용자 존재 여부 확인
        user = user_helper.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return {
            "user_id": user.id,
            "email": user.email,
            "role": getattr(user, 'role', 'user'),
            "is_active": getattr(user, 'is_active', True)
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 형식이 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )