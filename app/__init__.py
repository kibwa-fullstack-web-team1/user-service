from fastapi import FastAPI
from app.utils.db import engine, Base
from app.api import activity_router, user_router
from app.config.config import config_by_name

def create_app(config_name: str):
    app = FastAPI()

    # 설정 로드
    config = config_by_name[config_name]
    app.config = config

    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)

    # 라우터 등록
    app.include_router(activity_router.router)
    app.include_router(user_router.router)

    @app.get("/health")
    def health_check():
        return {"status": 200, "message": "OK"}

    @app.get("/")
    def root():
        return {"message": "Hello World"}

    return app
