"""
Modèle brief (table `briefs`) et table d'association BriefStudent (brief_students).

Un brief appartient à une session et peut être assigné à plusieurs étudiants.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship as sa_relationship
from sqlmodel import SQLModel, Field, Relationship

from app.models.session import Session
from app.models.user import User


class BriefStudent(SQLModel, table=True):
    """Lien many-to-many : un brief est assigné à un ou plusieurs étudiants."""
    __tablename__ = "brief_students"
    __table_args__ = (
        UniqueConstraint("brief_id", "student_id", name="uq_brief_student"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    brief_id: int = Field(foreign_key="briefs.id")
    student_id: int = Field(foreign_key="users.id")

    student: User = Relationship(back_populates="brief_links")


class Brief(SQLModel, table=True):
    """
    Brief (devoir) d'une session, assignable à un ou plusieurs étudiants (ou un groupe).
    """
    __tablename__ = "briefs"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=2, max_length=255)
    description: Optional[str] = Field(default=None)
    delivery_deadline: datetime = Field()
    order: int = Field(default=0)
    session_id: int = Field(foreign_key="sessions.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    session: Session = Relationship(back_populates="briefs")


# Relations many-to-many ajoutées après définition (évite résolution forward ref / List[])
BriefStudent.brief = sa_relationship("Brief", back_populates="student_links")
Brief.student_links = sa_relationship("BriefStudent", back_populates="brief")
