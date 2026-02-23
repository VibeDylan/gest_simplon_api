"""
Modèle inscription (table `enrollments`).

Table d'association entre Session et User (apprenant).
Contrainte unique (session_id, student_id) : une inscription par session et par apprenant.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class Enrollment(SQLModel, table=True):
    """
    Inscription d'un apprenant à une session.

    Un même apprenant ne peut être inscrit qu'une fois par session (contrainte
    uq_enrollment_session_student).

    Attributes:
        id: Clé primaire.
        session_id, student_id: Clés étrangères.
        enrolled_at: Date d'inscription.
        session, student: Relations.
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_enrollment_session_student"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.id")
    student_id: int = Field(foreign_key="users.id")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)

    session: "Session" = Relationship(back_populates="enrollments")
    student: "User" = Relationship(back_populates="enrollments")
