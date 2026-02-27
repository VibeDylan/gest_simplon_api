"""
Routeur principal API v1.

Agrège les sous-routeurs : users, formations, sessions, enrollments, briefs, groups.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.briefs import router as briefs_router
from app.api.v1.enrollment import router as enrollment_router
from app.api.v1.formations import router as formations_router
from app.api.v1.groups import router as groups_router
from app.api.v1.signatures import router as signatures_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(formations_router)
api_router.include_router(sessions_router)
api_router.include_router(signatures_router)
api_router.include_router(enrollment_router)
api_router.include_router(briefs_router)
api_router.include_router(groups_router)