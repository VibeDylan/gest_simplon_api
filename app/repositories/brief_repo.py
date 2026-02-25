"""
Repository CRUD pour l'entité Brief.

Encapsule l'accès en base (création, lecture, mise à jour, suppression)
et les listes par session_id / student_id.
"""
from typing import List, Optional

from sqlmodel import Session, select

from app.models.brief import Brief
from app.schemas.brief import BriefCreate, BriefUpdate


class BriefRepository:
    """
    Accès données pour les briefs.

    Utilise une session SQLModel injectée. Toutes les méthodes
    qui modifient les données font commit (create, update, delete).
    """
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: BriefCreate) -> Brief:
        brief = Brief(**data.model_dump())
        self.session.add(brief)
        self.session.commit()
        self.session.refresh(brief)
        return brief

    def get_by_id(self, id: int) -> Optional[Brief]:
        return self.session.get(Brief, id)

    def exists(self, id: int) -> bool:
        return self.get_by_id(id) is not None

    def list(self) -> List[Brief]:
        return self.session.exec(select(Brief)).all()

    def update(self, id: int, data: BriefUpdate) -> Optional[Brief]:
        brief = self.get_by_id(id)
        if brief is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(brief, key, value)
        self.session.commit()
        self.session.refresh(brief)
        return brief

    def delete(self, id: int) -> bool:
        brief = self.get_by_id(id)
        if brief is None:
            return False
        self.session.delete(brief)
        self.session.commit()
        return True

    def list_by_session_id(self, session_id: int) -> List[Brief]:
        return self.session.exec(select(Brief).where(Brief.session_id == session_id)).all()

    def list_by_student_id(self, student_id: int) -> List[Brief]:
        return self.session.exec(select(Brief).where(Brief.student_id == student_id)).all()

    def get_by_session_id_and_student_id(self, session_id: int, student_id: int) -> Optional[Brief]:
        return self.session.exec(select(Brief).where(Brief.session_id == session_id, Brief.student_id == student_id)).first()
    
