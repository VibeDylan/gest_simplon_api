"""
Routes groupes (CRUD et liste par session).
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session as SqlSession

from app.db.session import get_session
from app.repositories.group_repo import GroupRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.group import GroupCreate, GroupRead, GroupUpdate
from app.services.group_service import GroupService


router = APIRouter(prefix="/groups", tags=["groups"])


def get_group_service(session: SqlSession = Depends(get_session)) -> GroupService:
    return GroupService(
        GroupRepository(session),
        SessionRepository(session),
    )


@router.post("", response_model=GroupRead, status_code=201)
def create_group(
    data: GroupCreate,
    service: GroupService = Depends(get_group_service),
):
    """Crée un groupe (optionnellement avec student_ids)."""
    return service.create(data)


@router.get("/session/{session_id}", response_model=List[GroupRead])
def list_groups_by_session(
    session_id: int,
    service: GroupService = Depends(get_group_service),
):
    """Liste les groupes d'une session."""
    return service.list_by_session_id(session_id)


@router.get("/{id}", response_model=GroupRead)
def get_group(id: int, service: GroupService = Depends(get_group_service)):
    """Récupère un groupe par ID."""
    return service.get_by_id(id)


@router.patch("/{id}", response_model=GroupRead)
def update_group(
    id: int,
    data: GroupUpdate,
    service: GroupService = Depends(get_group_service),
):
    """Met à jour un groupe (nom et/ou liste des membres)."""
    return service.update(id, data)


@router.delete("/{id}", status_code=204)
def delete_group(id: int, service: GroupService = Depends(get_group_service)):
    """Supprime un groupe."""
    service.delete(id)
    return None
