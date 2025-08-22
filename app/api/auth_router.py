from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin, Token, User as UserSchema, RegisterResponse
from app.models import user as user_model
from app.utils.db import get_db
from app.utils import security
from app.helper import user_helper
from datetime import timedelta
import logging

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix = "/auth", tags = ["Auth"])

@router.post("/register", response_model = RegisterResponse)
def register(user : UserCreate, db : Session = Depends(get_db)) :
    logger.info(f"회원가입 시도: {user.email}")
    
    # 이메일 중복 검사
    existing_user = user_helper.get_user_by_email(db, user.email)
    if existing_user:
        logger.warning(f"회원가입 실패: 이메일 중복 - {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다."
        )
    
    # 사용자명 중복 검사
    existing_username = user_helper.get_user_by_username(db, user.username)
    if existing_username:
        logger.warning(f"회원가입 실패: 사용자명 중복 - {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다."
        )
    
    # 비밀번호 해시 적용
    hashed_password = security.hash_password(user.password)
    
    # 사용자 생성 (해시된 비밀번호 사용)
    user_data = UserCreate(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        password=hashed_password  # 해시된 비밀번호 전달
    )
    
    db_user = user_helper.create_user(db=db, user=user_data)
    
    logger.info(f"회원가입 성공: {user.email}, ID: {db_user.id}")
    
    # 회원가입 후 자동 로그인 (토큰 반환)
    access_token = security.create_access_token({"sub": str(db_user.id)})
    
    return RegisterResponse(
        message="회원가입이 완료되었습니다.",
        access_token=access_token,
        token_type="bearer",
        user_role=db_user.role.value,
        username=db_user.username
    )

@router.post("/login", response_model = Token)
def login(login_data : UserLogin, db : Session = Depends(get_db)) :
    logger.info(f"로그인 시도: {login_data.email}")
    
    user = user_helper.get_user_by_email(db = db, email = login_data.email)
    if not user or not security.verify_password(login_data.password, user.hashed_password) :
        logger.warning(f"로그인 실패: {login_data.email} - 잘못된 이메일 또는 비밀번호")
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "이메일 또는 비밀번호가 올바르지 않습니다.")
    
    access_token = security.create_access_token({"sub" : str(user.id)})
    
    logger.info(f"로그인 성공: {login_data.email}, ID: {user.id}")
    
    # 2024-08-18: user_role 필드 추가 - 사용자 역할을 응답에 포함
    return {
            "access_token" : access_token, 
            "token_type" : "bearer",
            "user_role": getattr(user, 'role', 'user'),  # 사용자 역할 추가
            "username": user.username
        }

@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """로그아웃 처리 - 토큰 검증 및 로그 기록"""
    try:
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("로그아웃 실패: Authorization 헤더 없음")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 필요합니다."
            )
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("로그아웃 실패: 잘못된 Authorization 헤더 형식")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization 헤더 형식이 올바르지 않습니다."
            )
        
        token = parts[1]
        
        # 토큰 검증 및 사용자 정보 추출
        try:
            payload = security.decode_access_token(token)
            if payload and payload.get("sub"):
                user_id = int(payload.get("sub"))
                user = user_helper.get_user_by_id(db, user_id)
                if user:
                    logger.info(f"로그아웃 성공: 사용자 ID {user_id} ({user.email})")
                else:
                    logger.warning(f"로그아웃: 사용자 ID {user_id}를 찾을 수 없음")
            else:
                logger.warning("로그아웃: 토큰에서 사용자 ID 추출 불가")
        except Exception as e:
            logger.warning(f"로그아웃: 토큰 검증 실패 - {str(e)}")
            # 토큰 검증 실패해도 로그아웃은 허용
        
        # TODO: 실제 운영환경에서는 토큰을 블랙리스트에 추가
        # 현재는 로그만 기록
        
        return {
            "message": "로그아웃되었습니다.",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그아웃 처리 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        )

@router.get("/verify")
async def verify_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """토큰 검증 및 사용자 정보 반환"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("토큰 검증 실패: Authorization 헤더 없음")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("토큰 검증 실패: 잘못된 Authorization 헤더 형식")
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
            logger.warning("토큰 검증 실패: 유효하지 않은 토큰")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
        
        user_id = int(payload.get("sub"))
        if not user_id:
            logger.warning("토큰 검증 실패: 토큰에서 사용자 ID 추출 불가")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에서 사용자 ID를 추출할 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
        
        # 사용자 존재 여부 확인
        user = user_helper.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"토큰 검증 실패: 사용자 ID {user_id}를 찾을 수 없음")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        logger.info(f"토큰 검증 성공: 사용자 ID {user_id}")
        return {
            "user_id": user.id,
            "email": user.email,
            "role": getattr(user, 'role', 'user'),
            "is_active": getattr(user, 'is_active', True),
            "username": user.username
        }
        
    except ValueError:
        logger.warning("토큰 검증 실패: 토큰 형식 오류")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 형식이 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )
    except Exception as e:
        logger.error(f"토큰 검증 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )