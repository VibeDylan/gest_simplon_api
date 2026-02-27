"""
Routes émargement (pad signature).

POST pour émarger (une signature = un jour).
GET par session + date (qui a signé ce jour) et par session + user (historique pad).
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as SqlSession

from app.db.session import get_session
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.signature_repo import SignatureRepository
from app.schemas.signature import SignatureCreate, SignatureRead
from app.services.signature_service import SignatureService


router = APIRouter(prefix="/signatures", tags=["signatures"])


def get_signature_service(session: SqlSession = Depends(get_session)) -> SignatureService:
    """Injecte session DB → repositories → service pour les routes signatures."""
    return SignatureService(
        SignatureRepository(session),
        SessionRepository(session),
        EnrollmentRepository(session),
    )


@router.post("", response_model=SignatureRead, status_code=201)
def create_signature(
    data: SignatureCreate,
    service: SignatureService = Depends(get_signature_service),
):
    """Émargement : enregistre une signature pour un jour (session_id, user_id, date optionnelle = aujourd'hui)."""
    signature = service.sign(data)
    return SignatureRead.model_validate(signature)


@router.get("/session/{session_id}/date/{date_str}", response_model=List[SignatureRead])
def list_signatures_by_session_and_date(
    session_id: int,
    date_str: str,
    service: SignatureService = Depends(get_signature_service),
):
    """Liste les signatures pour une session et un jour (qui a signé ce jour-là). Format date : YYYY-MM-DD."""
    try:
        sign_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(422, detail="Invalid date format, use YYYY-MM-DD")
    signatures = service.list_by_session_and_date(session_id, sign_date)
    return [SignatureRead.model_validate(s) for s in signatures]


@router.get("/session/{session_id}/user/{user_id}", response_model=List[SignatureRead])
def list_signatures_by_session_and_user(
    session_id: int,
    user_id: int,
    service: SignatureService = Depends(get_signature_service),
):
    """Liste les dates signées par un utilisateur pour une session (historique du pad)."""
    signatures = service.list_by_session_and_user(session_id, user_id)
    return [SignatureRead.model_validate(s) for s in signatures]


@router.get("/{id}", response_model=SignatureRead)
def get_signature(
    id: int,
    service: SignatureService = Depends(get_signature_service),
):
    """Retourne une signature par id."""
    signature = service.get_by_id(id)
    return SignatureRead.model_validate(signature)
