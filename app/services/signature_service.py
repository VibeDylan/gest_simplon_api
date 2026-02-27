"""
Service métier pour l'émargement (pad signature).

Règles : session existante, utilisateur inscrit (enrollment), date dans la période
session (start_date..end_date), au plus une signature par (session, user, date).
"""
from datetime import date
from typing import List

from app.core.errors import (
    SessionNotFound,
    SignatureAlreadyExistsForDate,
    SignatureDateOutsideSession,
    UserNotEnrolledInSession,
)
from app.models.signature import Signature
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.signature_repo import SignatureRepository
from app.schemas.signature import SignatureCreate


class SignatureService:
    """Orchestre repository signatures, session, enrollment et règles métier."""

    def __init__(
        self,
        signature_repo: SignatureRepository,
        session_repo: SessionRepository,
        enrollment_repo: EnrollmentRepository,
    ):
        self.signature_repo = signature_repo
        self.session_repo = session_repo
        self.enrollment_repo = enrollment_repo

    def sign(self, data: SignatureCreate) -> Signature:
        """
        Enregistre un émargement (un jour signé).
        Lève SessionNotFound, UserNotEnrolledInSession, SignatureDateOutsideSession,
        SignatureAlreadyExistsForDate.
        """
        session = self.session_repo.get_by_id(data.session_id)
        if session is None:
            raise SessionNotFound()
        sign_date = data.date if data.date is not None else date.today()

        start = session.start_date.date()
        end = session.end_date.date()
        if not (start <= sign_date <= end):
            raise SignatureDateOutsideSession()

        enrollment = self.enrollment_repo.get_by_session_id_and_student_id(
            data.session_id, data.user_id
        )
        if enrollment is None:
            raise UserNotEnrolledInSession()

        if self.signature_repo.exists_for_date(data.session_id, data.user_id, sign_date):
            raise SignatureAlreadyExistsForDate()

        return self.signature_repo.create(data.session_id, data.user_id, sign_date)

    def get_by_id(self, id: int) -> Signature:
        """Retourne une signature par id. Lève SignatureNotFound si absente."""
        from app.core.errors import SignatureNotFound

        sig = self.signature_repo.get_by_id(id)
        if sig is None:
            raise SignatureNotFound()
        return sig

    def list_by_session_and_date(
        self, session_id: int, sign_date: date
    ) -> List[Signature]:
        """Liste les signatures pour une session et un jour (qui a signé ce jour-là)."""
        if self.session_repo.get_by_id(session_id) is None:
            raise SessionNotFound()
        return self.signature_repo.list_by_session_and_date(session_id, sign_date)

    def list_by_session_and_user(
        self, session_id: int, user_id: int
    ) -> List[Signature]:
        """Liste les dates signées par un utilisateur pour une session (historique pad)."""
        if self.session_repo.get_by_id(session_id) is None:
            raise SessionNotFound()
        return self.signature_repo.list_by_session_and_user(session_id, user_id)
