"""
Routes inscriptions (CRUD et listes par session / étudiant).

CRUD enrollments et endpoints pour lister par session_id ou student_id.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.enrollement import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.services.enrollment_service import EnrollmentService


router = APIRouter(prefix="/enrollments", tags=["enrollments"])


def get_enrollment_service(session: Session = Depends(get_session)) -> EnrollmentService:
    """Injecte session DB → repositories (enrollment, session, user) → service."""
    return EnrollmentService(
        EnrollmentRepository(session),
        SessionRepository(session),
        UserRepository(session),
    )


@router.post("", response_model=EnrollmentRead, status_code=201)
def create_enrollment(
    data: EnrollmentCreate,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Crée une inscription (session_id, student_id)."""
    enrollment = service.create(data)
    return EnrollmentRead.model_validate(enrollment)


@router.get("", response_model=List[EnrollmentRead])
def list_enrollments(
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Liste toutes les inscriptions."""
    enrollments = service.list()
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get("/session/{session_id}", response_model=List[EnrollmentRead])
def list_enrollments_by_session_id(
    session_id: int,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Liste les inscriptions d'une session."""
    enrollments = service.list_by_session_id(session_id)
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get("/student/{student_id}", response_model=List[EnrollmentRead])
def list_enrollments_by_student_id(
    student_id: int,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Liste les inscriptions d'un étudiant."""
    enrollments = service.list_by_student_id(student_id)
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get("/{id}", response_model=EnrollmentRead)
def get_enrollment(
    id: int,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Récupère une inscription par ID."""
    enrollment = service.get_by_id(id)
    return EnrollmentRead.model_validate(enrollment)


@router.patch("/{id}", response_model=EnrollmentRead)
def update_enrollment(
    id: int,
    data: EnrollmentUpdate,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Met à jour une inscription par ID."""
    enrollment = service.update(id, data)
    return EnrollmentRead.model_validate(enrollment)


@router.delete("/{id}", status_code=204)
def delete_enrollment(
    id: int,
    service: EnrollmentService = Depends(get_enrollment_service),
):
    """Supprime une inscription par ID."""
    service.delete(id)
    return None
