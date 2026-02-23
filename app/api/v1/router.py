from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1.formations import router as formations_router
api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(formations_router, prefix="/formations", tags=["formations"])