from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 활동 유형 스키마
class ActivityTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class ActivityTypeCreate(ActivityTypeBase):
    pass

class ActivityType(ActivityTypeBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# 활동 로그 스키마
class ActivityLogBase(BaseModel):
    details: Optional[dict] = None

class ActivityLogCreate(ActivityLogBase):
    user_id: int
    activity_type_id: int

class ActivityLog(ActivityLogBase):
    id: int
    user_id: int
    activity_type_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# 활동 로그 조회 시, 관련된 활동 유형 정보까지 포함하는 상세 스키마
class ActivityLogWithDetails(ActivityLog):
    activity_type: ActivityType
