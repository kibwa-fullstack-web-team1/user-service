from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.db import Base, init_db
from app.api import user_router, auth_router, family_router
from app.config.config import config_by_name
from app.utils.logger import setup_logging

def create_app(config_name: str):
    app = FastAPI()

    # CORS 설정 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # 설정 로드 - () 추가하여 인스턴스화
    config = config_by_name[config_name]()
    app.config = config
    
    # 로깅 설정 초기화
    setup_logging()

    # 데이터베이스 초기화
    init_db()
    
    # engine을 다시 가져와서 사용
    from app.utils.db import engine
    Base.metadata.create_all(bind=engine)

    # 라우터 등록
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(family_router)

    @app.get("/health")
    def health_check():
        return {"status": 200, "message": "OK", "service": "user-service", "port": 8000}

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    return app
