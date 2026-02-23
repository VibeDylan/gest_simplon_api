"""
Service métier pour les sessions.

Orchestre le repository session et applique les règles métier :
vérification formation / formateur existants, ordre des dates, levée d'exceptions.
"""
from datetime import datetime
from typing import List

from app.core.errors import (
    FormationNotFound,
    SessionNotFound,
    SessionStartDateAfterEndDate,
    SessionStartDateAlreadyExists,
    SessionEndDateAlreadyExists,
    TeacherNotFound,
)
from app.models.session import Session
from app.repositories.formation_repo import FormationRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.session import SessionCreate, SessionUpdate


class SessionService:
    def __init__(
        self,
        repo: SessionRepository,
        formation_repo: FormationRepository,
        user_repo: UserRepository,
    ):
        self.repo = repo
        self.formation_repo = formation_repo
        self.user_repo = user_repo

    def create(self, data: SessionCreate) -> Session:
        """
        Crée une session.
        Lève FormationNotFound si la formation n'existe pas, TeacherNotFound si le formateur n'existe pas,
        SessionStartDateAfterEndDate si start_date >= end_date,
        SessionStartDateAlreadyExists / SessionEndDateAlreadyExists si une session existe déjà avec ces dates.
        """
        if self.formation_repo.get_by_id(data.formation_id) is None:
            raise FormationNotFound()
        if self.user_repo.get_by_id(data.teacher_id) is None:
            raise TeacherNotFound()
        if data.start_date >= data.end_date:
            raise SessionStartDateAfterEndDate()
        if self.repo.get_by_start_date(data.start_date) is not None:
            raise SessionStartDateAlreadyExists()
        if self.repo.get_by_end_date(data.end_date) is not None:
            raise SessionEndDateAlreadyExists()
        return self.repo.create(data)

    def get_by_id(self, id: int) -> Session:
        """Retourne la session d'id donné ou lève SessionNotFound."""
        session = self.repo.get_by_id(id)
        if session is None:
            raise SessionNotFound()
        return session

    def list(self, offset: int = 0, limit: int = 100) -> List[Session]:
        """Liste paginée de sessions (délègue au repo, pas d'exception si vide)."""
        return self.repo.list(offset=offset, limit=limit)

    def update(self, id: int, data: SessionUpdate) -> Session:
        """
        Met à jour une session (champs fournis uniquement).
        Lève SessionNotFound si absente, FormationNotFound/TeacherNotFound si ids invalides,
        SessionStartDateAfterEndDate si ordre des dates invalide.
        """
        session = self.repo.get_by_id(id)
        if session is None:
            raise SessionNotFound()
        if data.formation_id is not None and self.formation_repo.get_by_id(data.formation_id) is None:
            raise FormationNotFound()
        if data.teacher_id is not None and self.user_repo.get_by_id(data.teacher_id) is None:
            raise TeacherNotFound()
        if data.start_date is not None and data.end_date is not None:
            if data.start_date >= data.end_date:
                raise SessionStartDateAfterEndDate()
        elif data.start_date is not None:
            if data.start_date >= session.end_date:
                raise SessionStartDateAfterEndDate()
        elif data.end_date is not None:
            if session.start_date >= data.end_date:
                raise SessionStartDateAfterEndDate()
        updated = self.repo.update(id, data)
        if updated is None:
            raise SessionNotFound()
        return updated

    def delete(self, id: int) -> bool:
        """Supprime la session par id. Lève SessionNotFound si absente."""
        deleted = self.repo.delete(id)
        if not deleted:
            raise SessionNotFound()
        return deleted

    def list_by_formation_id(self, formation_id: int) -> List[Session]:
        """Retourne toutes les sessions pour une formation donnée (liste vide si aucune)."""
        return self.repo.list_by_formation_id(formation_id)

    def list_by_teacher_id(self, teacher_id: int) -> List[Session]:
        """Retourne toutes les sessions animées par un formateur donné (liste vide si aucune)."""
        return self.repo.list_by_teacher_id(teacher_id)

    def get_by_formation_id(self, formation_id: int) -> Session:
        """Retourne la première session pour cette formation. Lève SessionNotFound si aucune."""
        session = self.repo.get_by_formation_id(formation_id)
        if session is None:
            raise SessionNotFound()
        return session

    def get_by_teacher_id(self, teacher_id: int) -> Session:
        """Retourne la première session pour ce formateur. Lève SessionNotFound si aucune."""
        session = self.repo.get_by_teacher_id(teacher_id)
        if session is None:
            raise SessionNotFound()
        return session

    def get_by_start_date(self, start_date: datetime) -> Session:
        """Retourne la première session avec cette date de début. Lève SessionNotFound si aucune."""
        session = self.repo.get_by_start_date(start_date)
        if session is None:
            raise SessionNotFound()
        return session

    def get_by_end_date(self, end_date: datetime) -> Session:
        """Retourne la première session avec cette date de fin. Lève SessionNotFound si aucune."""
        session = self.repo.get_by_end_date(end_date)
        if session is None:
            raise SessionNotFound()
        return session

    def get_by_formation_id_and_teacher_id(
        self, formation_id: int, teacher_id: int
    ) -> Session:
        """Retourne la première session pour cette formation et ce formateur. Lève SessionNotFound si aucune."""
        session = self.repo.get_by_formation_id_and_teacher_id(
            formation_id, teacher_id
        )
        if session is None:
            raise SessionNotFound()
        return session
