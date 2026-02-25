"""
Modèles Group et GroupMember (tables `groups`, `group_members`).

Un groupe appartient à une session et contient plusieurs apprenants.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship as sa_relationship
from sqlmodel import SQLModel, Field, Relationship

from app.models.session import Session
from app.models.user import User


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

    session: Session = Relationship(back_populates="groups")


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

    student: User = Relationship(back_populates="group_memberships")


# Relations ajoutées après (évite List[] / Optional[] dans les annotations)
Group.members = sa_relationship("GroupMember", back_populates="group")
GroupMember.group = sa_relationship("Group", back_populates="members")
