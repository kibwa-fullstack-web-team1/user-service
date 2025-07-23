from fastapi import APIRouter
from app.api.user_router import router as user_router
from app.api.activity_router import router as activity_router
from app.api.auth_router import router as auth_router

router = APIRouter()

router.include_router(user_router)
router.include_router(activity_router)
router.include_router(auth_router)