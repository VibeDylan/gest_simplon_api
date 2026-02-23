"""
Routes utilisateurs (CRUD).

Une route exemple : POST pour créer un utilisateur (DTO entrée UserCreate, sortie UserRead).
"""
from fastapi import APIRouter, Depends

from app.db.session import get_session
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from sqlmodel import Session
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    """Injecte session → repository → service pour les routes users."""
    repo = UserRepository(session)
    return UserService(repo)


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """
    Crée un utilisateur.
    - **email** : unique, normalisé en minuscules
    - Lève 409 si l'email est déjà utilisé (EmailAlreadyUsed)
    """
    user = service.create(data)
    return UserRead.model_validate(user)

@router.get("", response_model=List[UserRead], status_code=200)
def list_users(
    service: UserService = Depends(get_user_service),
    offset: int = 0,
    limit: int = 100,
):
    """
    Liste les utilisateurs.
    """
    users = service.list(offset=offset, limit=limit)
    return [UserRead.model_validate(user) for user in users]

@router.get("/{id}", response_model=UserRead, status_code=200)
def get_user(
    id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Récupère un utilisateur par ID.
    """
    user = service.get_by_id(id)
    return UserRead.model_validate(user)

@router.patch("/{id}", response_model=UserRead, status_code=200)
def update_user(
    id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    """
    Met à jour un utilisateur par ID.
    - **email** : unique, normalisé en minuscules
    - Lève 409 si l'email est déjà utilisé (EmailAlreadyUsed)
    """
    user = service.update(id, data)
    return UserRead.model_validate(user)

@router.delete("/{id}", status_code=204)
def delete_user(
    id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Supprime un utilisateur par ID.
    """
    service.delete(id)
    return None