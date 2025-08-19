from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import httpx
from app.schemas.invitation_schema import (
    InvitationCodeCreate, 
    InvitationCodeResponse, 
    InvitationCodeDisplay,
    FamilyConnectRequest,
    FamilyConnectResponse,
    InvitationCodeStatus,
    FamilyMembersResponse,
    InvitationCodeListResponse,
    GroupInvitationCodeCreate,
    GroupInvitationCodeResponse
)
from app.models import user as user_model
from app.models.invitation import Invitation
from app.utils.db import get_db
from app.utils import security
from app.helper import invitation_helper
from datetime import datetime

router = APIRouter(prefix="/family", tags=["Family"])

# Notification service URL
NOTIFICATION_SERVICE_URL = "http://localhost:8002"

async def send_notification_to_service(endpoint: str, data: dict):
    """Notification service에 알림 요청을 보냅니다."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NOTIFICATION_SERVICE_URL}{endpoint}",
                json=data,
                timeout=10.0
            )
            if response.status_code == 200:
                print(f"알림 발송 성공: {endpoint}")
                return True
            else:
                print(f"알림 발송 실패: {endpoint}, 상태: {response.status_code}")
                return False
    except Exception as e:
        print(f"알림 서비스 호출 오류: {endpoint}, 오류: {str(e)}")
        return False

def get_current_user_id(request: Request, db: Session = Depends(get_db)) -> int:
    """현재 로그인한 사용자의 ID를 반환 (JWT 토큰에서 추출)"""
    auth_header = request.headers.get('Authorization')
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
        user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return user_id
        
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

@router.post("/invite-code", response_model=InvitationCodeResponse)
async def create_invitation_code(
    connection_data: InvitationCodeCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """초대코드 생성 (시니어만 가능)"""
    try:
        # 시니어 권한 확인
        user = db.query(user_model.User).filter(user_model.User.id == current_user_id).first()
        if not user or user.role != user_model.UserRole.senior:
            raise HTTPException(status_code=403, detail="시니어만 초대코드를 생성할 수 있습니다.")
        
        # 그룹 초대코드 생성
        if connection_data.is_group_code:
            invitation = invitation_helper.create_group_invitation_code(
                db=db,
                inviter_id=current_user_id,
                relationship_type_id=connection_data.relationship_type_id
            )
        else:
            # 기존 개별 초대코드 생성
            invitation = invitation_helper.create_invitation_code(
                db=db,
                inviter_id=current_user_id,
                invitee_email=connection_data.invitee_email,
                relationship_type_id=connection_data.relationship_type_id
            )
        
        # 알림 발송
        await send_notification_to_service("/api/v1/notifications/invite", {
            "inviter_id": current_user_id,
            "invitation_code": invitation.code,
            "notification_type": "family_invitation"
        })
        
        return invitation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초대코드 생성 실패: {str(e)}")

@router.post("/invite-code/group", response_model=GroupInvitationCodeResponse)
async def create_group_invitation_code(
    connection_data: GroupInvitationCodeCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """그룹 초대코드 생성 (시니어만 가능)"""
    try:
        # 시니어 권한 확인
        user = db.query(user_model.User).filter(user_model.User.id == current_user_id).first()
        if not user or user.role != user_model.UserRole.senior:
            raise HTTPException(status_code=403, detail="시니어만 그룹 초대코드를 생성할 수 있습니다.")
        
        # 그룹 초대코드 생성
        invitation = invitation_helper.create_group_invitation_code(
            db=db,
            inviter_id=current_user_id,
            max_guardians=connection_data.max_guardians,
            relationship_type_id=connection_data.relationship_type_id,
            expires_in_days=connection_data.expires_in_days
        )
        
        # 알림 발송
        await send_notification_to_service("/api/v1/notifications/invite", {
            "inviter_id": current_user_id,
            "invitation_code": invitation.code,
            "notification_type": "group_family_invitation"
        })
        
        return invitation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"그룹 초대코드 생성 실패: {str(e)}")

@router.get("/invite-code/{code}", response_model=InvitationCodeStatus)
def get_invitation_code_status(
    code: str,
    db: Session = Depends(get_db)
):
    """초대코드 상태 확인 (인증 불필요)"""
    invitation = invitation_helper.get_invitation_code_by_code(db, code)
    
    if not invitation:
        return InvitationCodeStatus(
            code=code,
            is_valid=False,
            is_used=False,
            expires_at=datetime.utcnow(),
            inviter_name=None,
            relationship_type=None
        )
    
    # 초대자 정보 조회
    inviter = db.query(user_model.User).filter(user_model.User.id == invitation.inviter_id).first()
    inviter_name = inviter.full_name or inviter.username if inviter else None
    
    # 관계 유형 정보 조회
    relationship_type = None
    if invitation.relationship_type_id:
        rel_type = db.query(user_model.RelationshipType).filter(
            user_model.RelationshipType.id == invitation.relationship_type_id
        ).first()
        relationship_type = rel_type.display_name_ko if rel_type else None
    
    return InvitationCodeStatus(
        code=invitation.code,
        is_valid=not invitation.is_used and invitation.expires_at > datetime.utcnow(),
        is_used=invitation.is_used,
        expires_at=invitation.expires_at,
        inviter_name=inviter_name,
        relationship_type=relationship_type
    )

@router.post("/connect", response_model=FamilyConnectResponse)
async def connect_family(
    connection_data: FamilyConnectRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """초대코드로 가족 연결 (보호자만 가능)"""
    try:
        family_relationship = invitation_helper.accept_invitation_code(
            db=db,
            code=connection_data.code,
            guardian_user_id=current_user_id,
            relationship_type_id=connection_data.relationship_type_id
        )
        
        # 가족 연결 시 notification 발송
        await send_notification_to_service("/api/v1/notifications/connect", {
            "guardian_id": current_user_id,
            "senior_id": family_relationship.senior_id,
            "relationship_type": family_relationship.relationship_type_id
        })

        return FamilyConnectResponse(
            success=True,
            message="가족 연결이 성공적으로 완료되었습니다.",
            family_relationship_id=family_relationship.id
        )
        
    except ValueError as e:
        return FamilyConnectResponse(
            success=False,
            message=str(e),
            family_relationship_id=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가족 연결 실패: {str(e)}")

@router.get("/members", response_model=FamilyMembersResponse)
def get_family_members(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """현재 사용자의 가족 구성원 조회"""
    try:
        family_members = invitation_helper.get_user_family_members(db, current_user_id)
        return FamilyMembersResponse(**family_members)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가족 구성원 조회 실패: {str(e)}")

@router.get("/invitations", response_model=InvitationCodeListResponse)
def get_user_invitations(
    skip: int = 0,
    limit: int = 100,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """사용자가 생성한 초대코드 목록 조회 (시니어만 가능)"""
    try:
        invitations = invitation_helper.get_user_invitations(db, current_user_id, skip, limit)
        total_count = len(invitations)
        
        return InvitationCodeListResponse(
            invitations=invitations,
            total_count=total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초대코드 목록 조회 실패: {str(e)}")

@router.delete("/invitations/{invitation_id}")
def delete_invitation(
    invitation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """초대코드 삭제 (생성자만 가능)"""
    try:
        invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
        
        if not invitation:
            raise HTTPException(status_code=404, detail="초대코드를 찾을 수 없습니다.")
        
        if invitation.inviter_id != current_user_id:
            raise HTTPException(status_code=403, detail="초대코드 삭제 권한이 없습니다.")
        
        db.delete(invitation)
        db.commit()
        
        return {"message": "초대코드가 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초대코드 삭제 실패: {str(e)}")

@router.post("/cleanup")
def cleanup_expired_invitations(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """만료된 초대코드 정리 (관리자 기능)"""
    try:
        # 실제로는 관리자 권한 확인 필요
        expired_count = invitation_helper.cleanup_expired_invitations(db)
        
        return {
            "message": f"{expired_count}개의 만료된 초대코드가 정리되었습니다.",
            "expired_count": expired_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"초대코드 정리 실패: {str(e)}")
