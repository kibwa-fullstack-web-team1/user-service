from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# TODO: 추후 환경 변수에서 데이터베이스 접속 정보를 가져오도록 수정해야 합니다.
from app.config.config import Config

SQLALCHEMY_DATABASE_URL = Config.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # 연결이 사용되기 전에 유효성 검사
    pool_recycle=3600 # 1시간마다 연결 재활용
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
