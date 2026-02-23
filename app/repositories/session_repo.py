"""
Repository CRUD pour l'entité Session.

Encapsule l'accès en base (création, lecture, mise à jour, suppression)
et la pagination. Méthodes de liste par formation_id / teacher_id.
"""
from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate

MAX_PAGE_SIZE = 100


class SessionRepository:
    """
    Accès données pour les sessions.

    Utilise une session SQLModel injectée. Toutes les méthodes
    qui modifient les données font commit (create, update, delete).
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: SessionCreate) -> SessionModel:
        """Crée une session en base et retourne l'instance avec id rempli."""
        session = SessionModel(**data.model_dump())
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session

    def get_by_id(self, id: int) -> Optional[SessionModel]:
        """Retourne la session d'id donné ou None."""
        return self.session.get(SessionModel, id)

    def exists(self, id: int) -> bool:
        """Retourne True si une session avec cet id existe, False sinon."""
        return self.get_by_id(id) is not None

    def list(self, offset: int = 0, limit: int = 100) -> List[SessionModel]:
        """Liste paginée de sessions. limit est plafonné à MAX_PAGE_SIZE."""
        limit = min(limit, MAX_PAGE_SIZE)
        return list(
            self.session.exec(
                select(SessionModel).offset(offset).limit(limit)
            ).all()
        )

    def update(self, id: int, data: SessionUpdate) -> Optional[SessionModel]:
        """Met à jour la session par id (champs fournis uniquement). Retourne None si absente."""
        session = self.get_by_id(id)
        if session is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(session, key, value)
        self.session.commit()
        self.session.refresh(session)
        return session

    def delete(self, id: int) -> bool:
        """Supprime la session par id. Retourne True si supprimée, False si non trouvée."""
        session = self.get_by_id(id)
        if session is None:
            return False
        self.session.delete(session)
        self.session.commit()
        return True

    def list_by_formation_id(self, formation_id: int) -> List[SessionModel]:
        """Retourne toutes les sessions pour une formation donnée."""
        return list(
            self.session.exec(
                select(SessionModel).where(SessionModel.formation_id == formation_id)
            ).all()
        )

    def list_by_teacher_id(self, teacher_id: int) -> List[SessionModel]:
        """Retourne toutes les sessions animées par un formateur donné."""
        return list(
            self.session.exec(
                select(SessionModel).where(SessionModel.teacher_id == teacher_id)
            ).all()
        )

    def get_by_formation_id(self, formation_id: int) -> Optional[SessionModel]:
        """Retourne la première session trouvée pour cette formation, ou None."""
        return self.session.exec(
            select(SessionModel).where(SessionModel.formation_id == formation_id)
        ).first()

    def get_by_teacher_id(self, teacher_id: int) -> Optional[SessionModel]:
        """Retourne la première session trouvée pour ce formateur, ou None."""
        return self.session.exec(
            select(SessionModel).where(SessionModel.teacher_id == teacher_id)
        ).first()

    def get_by_start_date(self, start_date: datetime) -> Optional[SessionModel]:
        """Retourne la première session avec cette date de début, ou None."""
        return self.session.exec(
            select(SessionModel).where(SessionModel.start_date == start_date)
        ).first()

    def get_by_end_date(self, end_date: datetime) -> Optional[SessionModel]:
        """Retourne la première session avec cette date de fin, ou None."""
        return self.session.exec(
            select(SessionModel).where(SessionModel.end_date == end_date)
        ).first()
