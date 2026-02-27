"""
Dépendances FastAPI partagées (auth, session DB).
"""
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(session))


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    """Récupère l'utilisateur actuel depuis le header Authorization: Bearer <token>."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = auth_header.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    repo = UserRepository(session)
    user = repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
