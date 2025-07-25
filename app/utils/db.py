from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import config_by_name # config_by_name 임포트

# 환경 설정 로드 (예: development 환경)
config = config_by_name['development']

DATABASE_URL = config.DATABASE_URL # Config에서 DATABASE_URL 가져오기

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
