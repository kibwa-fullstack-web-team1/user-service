from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.utils.db import Base

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, index=True, nullable=False)  # 8자리 초대코드
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 초대한 사용자 ID
    invitee_email = Column(String, nullable=True)  # 초대받은 이메일 (선택사항)
    relationship_type_id = Column(Integer, ForeignKey("relationship_types.id"), nullable=True)  # 관계 유형 ID
    is_used = Column(Boolean, default=False, nullable=False)  # 사용 여부 (개별 초대코드용)
    expires_at = Column(DateTime, nullable=False)  # 만료 시간
    created_at = Column(DateTime, server_default=func.now())  # 생성 시간
    used_at = Column(DateTime, nullable=True)  # 사용 시간 (개별 초대코드용)
    
    # 그룹 초대코드 관련 필드
    is_group_code = Column(Boolean, default=False, nullable=False)  # 그룹 초대코드 여부
    max_guardians = Column(Integer, default=10, nullable=True)  # 최대 보호자 수
    current_guardians = Column(Integer, default=0, nullable=True)  # 현재 연결된 보호자 수
    is_active = Column(Boolean, default=True, nullable=False)  # 그룹 초대코드 활성화 상태
    
    # 관계 설정
    inviter = relationship("User", foreign_keys=[inviter_id])
    relationship_type = relationship("RelationshipType")
