"""
Modèles Group et GroupMember (tables `groups`, `group_members`).

Un groupe appartient à une session et contient plusieurs apprenants.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


def _session_cls():
    from app.models.session import Session
    return Session


def _user_cls():
    from app.models.user import User
    return User


class Group(SQLModel, table=True):
    """
    Groupe d'apprenants au sein d'une session.

    Attributes:
        id: Clé primaire.
        session_id: Session à laquelle le groupe appartient.
        name: Nom du groupe.
        members: Liste des membres (User) via GroupMember.
    """
    __tablename__ = "groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.id")
    name: str = Field(min_length=1, max_length=255)

    session: _session_cls = Relationship(back_populates="groups")
    members: List["GroupMember"] = Relationship(back_populates="group")


class GroupMember(SQLModel, table=True):
    """
    Association groupe / apprenant (N–N).

    Un même étudiant peut être dans plusieurs groupes d'une session.
    """
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "student_id", name="uq_group_member"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id")
    student_id: int = Field(foreign_key="users.id")

    group: Optional[Group] = Relationship(back_populates="members")
    student: _user_cls = Relationship(back_populates="group_memberships")
