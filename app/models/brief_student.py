"""
Table d'association Brief <-> User (apprenants).

Un brief peut être assigné à un ou plusieurs étudiants (ou un groupe, résolu en liste d'ids).
"""
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class BriefStudent(SQLModel, table=True):
    """
    Lien many-to-many : un brief est assigné à un ou plusieurs étudiants.
    Utilisé comme link_model dans Brief.students et User.briefs.
    """
    __tablename__ = "brief_students"
    __table_args__ = (
        UniqueConstraint("brief_id", "student_id", name="uq_brief_student"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    brief_id: int = Field(foreign_key="briefs.id")
    student_id: int = Field(foreign_key="users.id")
