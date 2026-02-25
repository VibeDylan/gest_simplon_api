"""
Routes briefs (CRUD et listes par session / étudiant).
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session as SqlSession

from app.db.session import get_session
from app.repositories.brief_repo import BriefRepository
from app.repositories.group_repo import GroupRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.brief import BriefCreate, BriefRead, BriefUpdate
from app.services.brief_service import BriefService


router = APIRouter(prefix="/briefs", tags=["briefs"])


def get_brief_service(session: SqlSession = Depends(get_session)) -> BriefService:
    return BriefService(
        BriefRepository(session),
        SessionRepository(session),
        GroupRepository(session),
    )


@router.post("", response_model=BriefRead, status_code=201)
def create_brief(
    data: BriefCreate,
    service: BriefService = Depends(get_brief_service),
):
    """Crée un brief. Assignation via student_ids ou group_id (priorité à group_id)."""
    return service.create(data)


@router.get("", response_model=List[BriefRead])
def list_briefs(service: BriefService = Depends(get_brief_service)):
    """Liste tous les briefs."""
    return service.list()


@router.get("/session/{session_id}", response_model=List[BriefRead])
def list_briefs_by_session(
    session_id: int,
    service: BriefService = Depends(get_brief_service),
):
    """Liste les briefs d'une session."""
    return service.list_by_session_id(session_id)


@router.get("/student/{student_id}", response_model=List[BriefRead])
def list_briefs_by_student(
    student_id: int,
    service: BriefService = Depends(get_brief_service),
):
    """Liste les briefs assignés à un étudiant."""
    return service.list_by_student_id(student_id)


@router.get("/{id}", response_model=BriefRead)
def get_brief(id: int, service: BriefService = Depends(get_brief_service)):
    """Récupère un brief par ID."""
    return service.get_by_id(id)


@router.patch("/{id}", response_model=BriefRead)
def update_brief(
    id: int,
    data: BriefUpdate,
    service: BriefService = Depends(get_brief_service),
):
    """Met à jour un brief (champs fournis). student_ids ou group_id pour réassigner."""
    return service.update(id, data)


@router.delete("/{id}", status_code=204)
def delete_brief(id: int, service: BriefService = Depends(get_brief_service)):
    """Supprime un brief."""
    service.delete(id)
    return None
