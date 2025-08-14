from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import config_by_name

# 환경 설정 로드 함수
def get_config():
    return config_by_name['development']()

# 데이터베이스 연결 함수
def create_db_engine():
    config = get_config()
    if not config.DATABASE_URL:
        raise ValueError("DATABASE_URL이 설정되지 않았습니다. 환경변수를 확인해주세요.")
    
    return create_engine(
        config.DATABASE_URL,
        pool_pre_ping=True,  # 연결이 사용되기 전에 유효성을 검사
        pool_recycle=3600,    # 1시간마다 연결을 재활용
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        }
    )

# 전역 변수 초기화
engine = None
SessionLocal = None
Base = declarative_base()

def init_db():
    """데이터베이스 초기화"""
    global engine, SessionLocal
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()