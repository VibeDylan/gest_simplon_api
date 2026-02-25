"""
Service métier pour les groupes.
"""
from typing import List

from app.core.errors import GroupNotFound, SessionNotFound
from app.models.group import Group
from app.repositories.group_repo import GroupRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.group import GroupCreate, GroupRead, GroupUpdate


def _group_to_read(group: Group) -> GroupRead:
    """Construit GroupRead avec student_ids à partir des membres."""
    student_ids = [m.student_id for m in group.members]
    return GroupRead(
        id=group.id,
        session_id=group.session_id,
        name=group.name,
        student_ids=student_ids,
    )


class GroupService:
    def __init__(
        self,
        group_repo: GroupRepository,
        session_repo: SessionRepository,
    ):
        self.group_repo = group_repo
        self.session_repo = session_repo

    def create(self, data: GroupCreate) -> GroupRead:
        if self.session_repo.get_by_id(data.session_id) is None:
            raise SessionNotFound()
        group = self.group_repo.create(data)
        return _group_to_read(group)

    def get_by_id(self, id: int) -> GroupRead:
        group = self.group_repo.get_by_id(id)
        if group is None:
            raise GroupNotFound()
        return _group_to_read(group)

    def list_by_session_id(self, session_id: int) -> List[GroupRead]:
        groups = self.group_repo.list_by_session_id(session_id)
        return [_group_to_read(g) for g in groups]

    def update(self, id: int, data: GroupUpdate) -> GroupRead:
        group = self.group_repo.get_by_id(id)
        if group is None:
            raise GroupNotFound()
        student_ids = data.student_ids if data.student_ids is not None else None
        updated = self.group_repo.update(id, data, student_ids=student_ids)
        if updated is None:
            raise GroupNotFound()
        return _group_to_read(updated)

    def delete(self, id: int) -> bool:
        if not self.group_repo.get_by_id(id):
            raise GroupNotFound()
        return self.group_repo.delete(id)
