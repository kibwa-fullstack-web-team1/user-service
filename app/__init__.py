from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.db import Base, init_db
from app.api import user_router, auth_router
from app.config.config import config_by_name

def create_app(config_name: str):
    app = FastAPI()

    # CORS 설정 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 설정 로드
    config = config_by_name[config_name]
    app.config = config

    # 데이터베이스 초기화
    init_db()
    
    # engine을 다시 가져와서 사용
    from app.utils.db import engine
    Base.metadata.create_all(bind=engine)

    # 라우터 등록
    app.include_router(user_router)
    app.include_router(auth_router)

    @app.get("/health")
    def health_check():
        return {"status": 200, "message": "OK"}

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    return app
