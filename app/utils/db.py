from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    from app.models import user, relationship_type
    
    # 모든 모델을 import하여 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 기본 관계 타입 데이터 삽입
    db = SessionLocal()
    try:
        # 기본 관계 타입이 없으면 생성
        existing_types = db.query(relationship_type.RelationshipType).all()
        if not existing_types:
            default_types = [
                relationship_type.RelationshipType(
                    name="부모-자녀",
                    description="부모와 자녀 간의 관계"
                ),
                relationship_type.RelationshipType(
                    name="배우자",
                    description="부부 간의 관계"
                ),
                relationship_type.RelationshipType(
                    name="친척",
                    description="친척 간의 관계"
                ),
                relationship_type.RelationshipType(
                    name="기타",
                    description="기타 가족 관계"
                )
            ]
            
            for rel_type in default_types:
                db.add(rel_type)
            
            db.commit()
            print("기본 관계 타입이 생성되었습니다.")
        else:
            print("기본 관계 타입이 이미 존재합니다.")
            
    except Exception as e:
        print(f"기본 관계 타입 생성 중 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

def create_tables():
    """테이블만 생성 (데이터 삽입 없음)"""
    from app.models import user, relationship_type
    Base.metadata.create_all(bind=engine)
    print("모든 테이블이 생성되었습니다.")

def drop_tables():
    """모든 테이블 삭제 (주의: 개발 환경에서만 사용)"""
    Base.metadata.drop_all(bind=engine)
    print("모든 테이블이 삭제되었습니다.")