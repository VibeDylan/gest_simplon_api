"""
Repository CRUD pour l'entité Brief.

Encapsule l'accès en base (création avec student_ids, lecture, mise à jour, suppression)
et les listes par session_id / student_id.
"""
from typing import List, Optional

from sqlmodel import Session, select

from app.models.brief import Brief
from app.models.brief_student import BriefStudent
from app.schemas.brief import BriefCreate, BriefUpdate


class BriefRepository:
    """
    Accès données pour les briefs.

    Utilise une session SQLModel injectée. create() attend que student_ids
    soit déjà résolu (par le service, éventuellement via group_id).
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: BriefCreate, student_ids: List[int]) -> Brief:
        """Crée un brief et les liaisons brief_students. student_ids déjà résolu (ex. par groupe)."""
        payload = data.model_dump(exclude={"student_ids", "group_id"})
        brief = Brief(**payload)
        self.session.add(brief)
        self.session.commit()
        self.session.refresh(brief)
        for sid in student_ids:
            self.session.add(BriefStudent(brief_id=brief.id, student_id=sid))
        if student_ids:
            self.session.commit()
            self.session.refresh(brief)
        return brief

    def get_by_id(self, id: int) -> Optional[Brief]:
        return self.session.get(Brief, id)

    def exists(self, id: int) -> bool:
        return self.get_by_id(id) is not None

    def list(self) -> List[Brief]:
        return list(self.session.exec(select(Brief)).all())

    def list_by_session_id(self, session_id: int) -> List[Brief]:
        return list(
            self.session.exec(select(Brief).where(Brief.session_id == session_id)).all()
        )

    def list_by_student_id(self, student_id: int) -> List[Brief]:
        return list(
            self.session.exec(
                select(Brief)
                .join(BriefStudent, Brief.id == BriefStudent.brief_id)
                .where(BriefStudent.student_id == student_id)
            ).all()
        )

    def update(self, id: int, data: BriefUpdate, student_ids: Optional[List[int]] = None) -> Optional[Brief]:
        brief = self.get_by_id(id)
        if brief is None:
            return None
        payload = data.model_dump(exclude_unset=True, exclude={"student_ids", "group_id"})
        for key, value in payload.items():
            setattr(brief, key, value)
        if student_ids is not None:
            existing = list(
                self.session.exec(select(BriefStudent).where(BriefStudent.brief_id == id))
            )
            for link in existing:
                self.session.delete(link)
            for sid in student_ids:
                self.session.add(BriefStudent(brief_id=id, student_id=sid))
        self.session.commit()
        self.session.refresh(brief)
        return brief

    def delete(self, id: int) -> bool:
        brief = self.get_by_id(id)
        if brief is None:
            return False
        for link in self.session.exec(select(BriefStudent).where(BriefStudent.brief_id == id)).all():
            self.session.delete(link)
        self.session.delete(brief)
        self.session.commit()
        return True
