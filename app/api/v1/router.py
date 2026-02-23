from fastapi import APIRouter

from app.api.v1.enrollment import router as enrollment_router
from app.api.v1.formations import router as formations_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(formations_router, prefix="/formations", tags=["formations"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
api_router.include_router(enrollment_router, prefix="/enrollments", tags=["enrollments"])