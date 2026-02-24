"""
Service métier pour les inscriptions.

Orchestre les repositories (enrollment, session, user) et applique les règles métier :
existence session/apprenant, capacité non dépassée, unicité (session_id, student_id).
"""
from typing import List

from app.core.errors import (
    EnrollmentAlreadyExists,
    EnrollmentNotFound,
    EnrollmentSessionFull,
    SessionNotFound,
    UserNotFound,
)
from app.models.enrollment import Enrollment
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.enrollement import EnrollmentCreate, EnrollmentUpdate


class EnrollmentService:
    """
    Service métier pour les inscriptions.

    Orchestre les repositories (enrollment, session, user) et applique les règles métier :
    session et apprenant existants, capacité non dépassée, unicité (session_id, student_id).
    """
    def __init__(
        self,
        repo: EnrollmentRepository,
        session_repo: SessionRepository,
        user_repo: UserRepository,
    ):
        """Initialise le service avec les repositories (enrollment, session, user) injectés."""
        self.repo = repo
        self.session_repo = session_repo
        self.user_repo = user_repo

    def create(self, data: EnrollmentCreate) -> Enrollment:
        """
        Crée une inscription.
        Lève SessionNotFound si la session n'existe pas, UserNotFound si l'apprenant n'existe pas,
        EnrollmentSessionFull si la session est pleine, EnrollmentAlreadyExists si déjà inscrit.
        """
        session = self.session_repo.get_by_id(data.session_id)
        if session is None:
            raise SessionNotFound()
        if self.user_repo.get_by_id(data.student_id) is None:
            raise UserNotFound()
        current_count = len(self.repo.list_by_session_id(data.session_id))
        if current_count >= session.capacity_max:
            raise EnrollmentSessionFull()
        if self.repo.get_by_session_id_and_student_id(data.session_id, data.student_id) is not None:
            raise EnrollmentAlreadyExists()
        return self.repo.create(data)
    
    def get_by_id(self, id: int) -> Enrollment:
        """Retourne l'inscription d'id donné ou lève EnrollmentNotFound."""
        enrollment = self.repo.get_by_id(id)
        if not enrollment:
            raise EnrollmentNotFound()
        return enrollment
    
    def list(self) -> List[Enrollment]:
        """Liste toutes les inscriptions."""
        return self.repo.list()
    
    def update(self, id: int, data: EnrollmentUpdate) -> Enrollment:
        """Met à jour l'inscription par id (champs fournis uniquement). Lève EnrollmentNotFound si absente."""
        enrollment = self.repo.update(id, data)
        if enrollment is None:
            raise EnrollmentNotFound()
        return enrollment
    
    def delete(self, id: int) -> bool:
        """Supprime l'inscription par id. Retourne True si supprimée, False si non trouvée."""
        return self.repo.delete(id)
    
    def list_by_session_id(self, session_id: int) -> List[Enrollment]:
        """Retourne toutes les inscriptions pour une session donnée."""
        return self.repo.list_by_session_id(session_id)

    def list_by_student_id(self, student_id: int) -> List[Enrollment]:
        """Retourne toutes les inscriptions pour un étudiant donné."""
        return self.repo.list_by_student_id(student_id)
    
    def get_by_session_id_and_student_id(self, session_id: int, student_id: int) -> Enrollment:
        """Retourne l'inscription pour une session et un étudiant donnés. Lève EnrollmentNotFound si absente."""
        enrollment = self.repo.get_by_session_id_and_student_id(session_id, student_id)
        if enrollment is None:
            raise EnrollmentNotFound()
        return enrollment