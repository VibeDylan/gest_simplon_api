"""
Routes sessions (CRUD et listes par formation / formateur / dates).

CRUD sessions et endpoints pour lister par formation_id, teacher_id,
ou récupérer par date de début / fin.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as SqlSession
from typing import List

from app.db.session import get_session
from app.repositories.formation_repo import FormationRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.session_service import SessionService


router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(
    session: SqlSession = Depends(get_session),
) -> SessionService:
    """Injecte session DB → repositories → service pour les routes sessions."""
    return SessionService(
        SessionRepository(session),
        FormationRepository(session),
        UserRepository(session),
    )


@router.post("", response_model=SessionRead, status_code=201)
def create_session(
    data: SessionCreate,
    service: SessionService = Depends(get_session_service),
):
    """Crée une session."""
    session = service.create(data)
    return SessionRead.model_validate(session)


@router.get("", response_model=List[SessionRead])
def list_sessions(
    service: SessionService = Depends(get_session_service),
    offset: int = 0,
    limit: int = 100,
):
    """Liste paginée de sessions."""
    sessions = service.list(offset=offset, limit=limit)
    return [SessionRead.model_validate(s) for s in sessions]


# Routes avec segments fixes avant /{id} pour éviter que "formation", "teacher", etc. soient pris pour un id
@router.get("/formation/{formation_id}", response_model=List[SessionRead])
def list_sessions_by_formation_id(
    formation_id: int,
    service: SessionService = Depends(get_session_service),
):
    """Liste les sessions d'une formation."""
    sessions = service.list_by_formation_id(formation_id)
    return [SessionRead.model_validate(s) for s in sessions]


@router.get("/teacher/{teacher_id}", response_model=List[SessionRead])
def list_sessions_by_teacher_id(
    teacher_id: int,
    service: SessionService = Depends(get_session_service),
):
    """Liste les sessions d'un formateur."""
    sessions = service.list_by_teacher_id(teacher_id)
    return [SessionRead.model_validate(s) for s in sessions]


@router.get("/formation/{formation_id}/teacher/{teacher_id}", response_model=SessionRead)
def get_session_by_formation_id_and_teacher_id(
    formation_id: int,
    teacher_id: int,
    service: SessionService = Depends(get_session_service),
):
    """Retourne la première session pour cette formation et ce formateur."""
    session = service.get_by_formation_id_and_teacher_id(formation_id, teacher_id)
    return SessionRead.model_validate(session)


@router.get("/start_date/{start_date_str}", response_model=SessionRead)
def get_session_by_start_date(
    start_date_str: str,
    service: SessionService = Depends(get_session_service),
):
    """Retourne la première session avec cette date de début (format ISO, ex. 2025-01-15T09:00:00)."""
    try:
        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, detail="Invalid datetime format, use ISO format (e.g. 2025-01-15T09:00:00)")
    session = service.get_by_start_date(start_date)
    return SessionRead.model_validate(session)


@router.get("/end_date/{end_date_str}", response_model=SessionRead)
def get_session_by_end_date(
    end_date_str: str,
    service: SessionService = Depends(get_session_service),
):
    """Retourne la première session avec cette date de fin (format ISO)."""
    try:
        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, detail="Invalid datetime format, use ISO format (e.g. 2025-01-15T18:00:00)")
    session = service.get_by_end_date(end_date)
    return SessionRead.model_validate(session)


@router.get("/{id}", response_model=SessionRead)
def get_session(
    id: int,
    service: SessionService = Depends(get_session_service),
):
    """Retourne une session par id."""
    session = service.get_by_id(id)
    return SessionRead.model_validate(session)


@router.patch("/{id}", response_model=SessionRead)
def update_session(
    id: int,
    data: SessionUpdate,
    service: SessionService = Depends(get_session_service),
):
    """Met à jour une session."""
    session = service.update(id, data)
    return SessionRead.model_validate(session)


@router.delete("/{id}", status_code=204)
def delete_session(
    id: int,
    service: SessionService = Depends(get_session_service),
):
    """Supprime une session."""
    service.delete(id)
