from typing import List
from app.models.enrollment import Enrollment
from app.repositories.enrollment_repo import EnrollmentRepository
from app.schemas.enrollement import EnrollmentCreate, EnrollmentUpdate
from app.core.errors import EnrollmentNotFound, EnrollmentAlreadyExists

class EnrollmentService:
    """
    Service métier pour les inscriptions.

    Orchestre le repository et applique les règles métier (unicité de l'inscription).
    """
    def __init__(self, repo: EnrollmentRepository):
        self.repo = repo

    def create(self, data: EnrollmentCreate) -> Enrollment:
        """Crée une inscription. Lève EnrollmentAlreadyExists si l'inscription existe déjà."""
        if self.repo.get_by_session_id_and_student_id(data.session_id, data.student_id) is not None:
            raise EnrollmentAlreadyExists()
        if self.repo.get_by_session_id(data.session_id) is not None:
            raise EnrollmentAlreadyExists()
        if self.repo.get_by_student_id(data.student_id) is not None:
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
        """Met à jour l'inscription par id (champs fournis uniquement). Retourne None si absente."""
        return self.repo.update(id, data)
    
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
        """Retourne l'inscription pour une session et un étudiant donnés."""
        return self.repo.get_by_session_id_and_student_id(session_id, student_id)