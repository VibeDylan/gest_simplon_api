"""
Service métier pour les briefs.

Orchestre le repository, résout group_id -> student_ids, et lève BriefNotFound / SessionNotFound.
"""
from typing import List

from app.core.errors import BriefNotFound, GroupNotFound, SessionNotFound
from app.models.brief import Brief
from app.repositories.brief_repo import BriefRepository
from app.repositories.group_repo import GroupRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.brief import BriefCreate, BriefRead, BriefUpdate


def _brief_to_read(brief: Brief) -> BriefRead:
    """Construit BriefRead avec student_ids à partir des relations chargées."""
    student_ids = [link.student_id for link in brief.student_links]
    return BriefRead(
        id=brief.id,
        title=brief.title,
        description=brief.description,
        delivery_deadline=brief.delivery_deadline,
        order=brief.order,
        session_id=brief.session_id,
        student_ids=student_ids,
        created_at=brief.created_at,
        updated_at=brief.updated_at,
    )


class BriefService:
    def __init__(
        self,
        brief_repo: BriefRepository,
        session_repo: SessionRepository,
        group_repo: GroupRepository,
    ):
        self.brief_repo = brief_repo
        self.session_repo = session_repo
        self.group_repo = group_repo

    def _resolve_student_ids(self, student_ids: List[int] | None, group_id: int | None) -> List[int]:
        """Retourne la liste des student_ids (group_id prioritaire)."""
        if group_id is not None:
            group = self.group_repo.get_by_id(group_id)
            if group is None:
                raise GroupNotFound()
            return self.group_repo.get_student_ids(group_id)
        return student_ids or []

    def create(self, data: BriefCreate) -> BriefRead:
        if self.session_repo.get_by_id(data.session_id) is None:
            raise SessionNotFound()
        student_ids = self._resolve_student_ids(data.student_ids, data.group_id)
        brief = self.brief_repo.create(data, student_ids)
        return _brief_to_read(brief)

    def get_by_id(self, id: int) -> BriefRead:
        brief = self.brief_repo.get_by_id(id)
        if brief is None:
            raise BriefNotFound()
        return _brief_to_read(brief)

    def list(self) -> List[BriefRead]:
        briefs = self.brief_repo.list()
        return [_brief_to_read(b) for b in briefs]

    def list_by_session_id(self, session_id: int) -> List[BriefRead]:
        briefs = self.brief_repo.list_by_session_id(session_id)
        return [_brief_to_read(b) for b in briefs]

    def list_by_student_id(self, student_id: int) -> List[BriefRead]:
        briefs = self.brief_repo.list_by_student_id(student_id)
        return [_brief_to_read(b) for b in briefs]

    def update(self, id: int, data: BriefUpdate) -> BriefRead:
        brief = self.brief_repo.get_by_id(id)
        if brief is None:
            raise BriefNotFound()
        student_ids = None
        if data.student_ids is not None:
            student_ids = data.student_ids
        elif data.group_id is not None:
            student_ids = self._resolve_student_ids(None, data.group_id)
        updated = self.brief_repo.update(id, data, student_ids=student_ids)
        if updated is None:
            raise BriefNotFound()
        return _brief_to_read(updated)

    def delete(self, id: int) -> bool:
        if not self.brief_repo.exists(id):
            raise BriefNotFound()
        return self.brief_repo.delete(id)
