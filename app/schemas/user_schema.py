from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    phone_number: Optional[str] = None # 전화번호 필드 추가
    hashed_password: str # 추가

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None # 전화번호 필드 추가
    hashed_password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel) :
    email : str
    password : str

class Token(BaseModel) :
    access_token : str
    token_type : str = "bearer"