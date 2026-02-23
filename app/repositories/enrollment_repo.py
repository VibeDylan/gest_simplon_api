from typing import List, Optional

from sqlmodel import Session, select

from app.models.enrollment import Enrollment
from app.schemas.enrollement import EnrollmentCreate, EnrollmentUpdate


class EnrollmentRepository:
    """
    Repository CRUD pour l'entité Enrollment.

    Encapsule l'accès en base (création, lecture, mise à jour, suppression).
    """
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: EnrollmentCreate) -> Enrollment:
        """Crée une inscription en base et retourne l'instance avec id rempli."""
        enrollment = Enrollment(**data.model_dump())
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def get_by_id(self, id: int) -> Optional[Enrollment]:
        """Retourne l'inscription d'id donné ou None."""
        return self.session.get(Enrollment, id)

    def exists(self, id: int) -> bool:
        """Retourne True si une inscription avec cet id existe, False sinon."""
        return self.get_by_id(id) is not None

    def list(self) -> List[Enrollment]:
        """Liste toutes les inscriptions."""
        return self.session.exec(select(Enrollment)).all()

    def update(self, id: int, data: EnrollmentUpdate) -> Optional[Enrollment]:
        """Met à jour l'inscription par id (champs fournis uniquement). Retourne None si absente."""
        enrollment = self.get_by_id(id)
        if enrollment is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(enrollment, key, value)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def delete(self, id: int) -> bool:
        """Supprime l'inscription par id. Retourne True si supprimée, False si non trouvée."""
        enrollment = self.get_by_id(id)
        if enrollment is None:
            return False
        self.session.delete(enrollment)
        self.session.commit()
        return True

    def list_by_session_id(self, session_id: int) -> List[Enrollment]:
        """Retourne toutes les inscriptions pour une session donnée."""
        return self.session.exec(select(Enrollment).where(Enrollment.session_id == session_id)).all()

    def list_by_student_id(self, student_id: int) -> List[Enrollment]:
        """Retourne toutes les inscriptions pour un étudiant donné."""
        return self.session.exec(select(Enrollment).where(Enrollment.student_id == student_id)).all()

    def get_by_session_id_and_student_id(self, session_id: int, student_id: int) -> Optional[Enrollment]:
        """Retourne l'inscription pour une session et un étudiant donnés."""
        return self.session.exec(select(Enrollment).where(Enrollment.session_id == session_id, Enrollment.student_id == student_id)).first()
