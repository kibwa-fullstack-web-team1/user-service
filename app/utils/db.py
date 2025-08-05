from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import config_by_name

# 환경 설정 로드 (예: development 환경)
config = config_by_name['development']

DATABASE_URL = config.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 연결이 사용되기 전에 유효성을 검사
    pool_recycle=3600    # 1시간마다 연결을 재활용
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()