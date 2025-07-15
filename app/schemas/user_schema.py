from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    hashed_password: str # 추가

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
