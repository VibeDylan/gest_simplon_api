"""
Repository CRUD pour Group et GroupMember.
"""
from typing import List, Optional

from sqlmodel import Session, select

from app.models.group import Group, GroupMember
from app.schemas.group import GroupCreate, GroupUpdate


class GroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: GroupCreate) -> Group:
        group = Group(session_id=data.session_id, name=data.name.strip())
        self.session.add(group)
        self.session.commit()
        self.session.refresh(group)
        student_ids = data.student_ids or []
        for sid in student_ids:
            self.session.add(GroupMember(group_id=group.id, student_id=sid))
        if student_ids:
            self.session.commit()
            self.session.refresh(group)
        return group

    def get_by_id(self, id: int) -> Optional[Group]:
        return self.session.get(Group, id)

    def list_by_session_id(self, session_id: int) -> List[Group]:
        return list(
            self.session.exec(select(Group).where(Group.session_id == session_id)).all()
        )

    def get_student_ids(self, group_id: int) -> List[int]:
        """Retourne la liste des student_id du groupe (pour assigner un brief au groupe)."""
        rows = self.session.exec(
            select(GroupMember.student_id).where(GroupMember.group_id == group_id)
        ).all()
        return list(rows)

    def update(self, id: int, data: GroupUpdate, student_ids: Optional[List[int]] = None) -> Optional[Group]:
        group = self.get_by_id(id)
        if group is None:
            return None
        if data.name is not None:
            group.name = data.name.strip()
        if student_ids is not None:
            existing = list(
                self.session.exec(select(GroupMember).where(GroupMember.group_id == id))
            )
            for m in existing:
                self.session.delete(m)
            for sid in student_ids:
                self.session.add(GroupMember(group_id=id, student_id=sid))
        self.session.commit()
        self.session.refresh(group)
        return group

    def delete(self, id: int) -> bool:
        group = self.get_by_id(id)
        if group is None:
            return False
        for m in self.session.exec(select(GroupMember).where(GroupMember.group_id == id)).all():
            self.session.delete(m)
        self.session.delete(group)
        self.session.commit()
        return True
