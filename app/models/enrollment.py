from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class Enrollment(SQLModel, table=True):
    """Table d'association Session <-> Apprenants (User). Un apprenant ne peut être inscrit qu'une fois par session."""

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
