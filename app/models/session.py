"""
Modèle session (table `sessions`).

Une session est une instance d'une formation, animée par un formateur,
avec des dates, une capacité max et un statut. Les apprenants s'y inscrivent via Enrollment.
"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.utils.enum import SessionStatus
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.brief import Brief
    from app.models.enrollment import Enrollment
    from app.models.formation import Formation
    from app.models.group import Group
    from app.models.user import User


def _formation_cls():
    from app.models.formation import Formation
    return Formation


def _user_cls():
    from app.models.user import User
    return User


def _enrollment_cls():
    from app.models.enrollment import Enrollment
    return Enrollment


class Session(SQLModel, table=True):
    """
    Session de formation (créneau dans le temps).

    Attributes:
        id: Clé primaire.
        formation_id: Formation concernée.
        teacher_id: Formateur (User) qui anime la session.
        start_date, end_date: Période de la session.
        capacity_max: Nombre max de places (≥ 1).
        status: SessionStatus.
        formation: Formation.
        teacher: User.
        enrollments: List[Enrollment].
    """

    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    formation_id: int = Field(foreign_key="formations.id")
    teacher_id: int = Field(foreign_key="users.id")
    start_date: datetime
    end_date: datetime
    capacity_max: int = Field(ge=1, default=1)
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)

    # Callables pour résolution différée (évite KeyError "'Formation'" avec Python 3.14)
    formation: _formation_cls = Relationship(back_populates="sessions")
    teacher: _user_cls = Relationship(back_populates="taught_sessions")
    enrollments: _enrollment_cls = Relationship(back_populates="session")
    briefs: List["Brief"] = Relationship(back_populates="session")
    groups: List["Group"] = Relationship(back_populates="session")
