"""
Modèle utilisateur (table `users`).

Représente un utilisateur du système : admin, formateur (trainer) ou apprenant (learner).
Lié aux sessions qu'il anime (taught_sessions) et aux inscriptions (enrollments).
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from app.utils.enum import Role


def _session_cls():
    from app.models.session import Session
    return Session


def _enrollment_cls():
    from app.models.enrollment import Enrollment
    return Enrollment


class User(SQLModel, table=True):
    """
    Utilisateur : admin, formateur ou apprenant.

    Attributes:
        id: Clé primaire auto-générée.
        email: Adresse unique, indexée.
        first_name, last_name: Nom (min 2 caractères).
        registered_at, updated_at: Horodatage création / mise à jour.
        role: Rôle (admin, trainer, learner).
        taught_sessions: Sessions dont il est formateur.
        enrollments: Inscriptions en tant qu'apprenant.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    hashed_password: str = Field(min_length=8)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    role: Role = Field(default=Role.LEARNER)

    taught_sessions: _session_cls = Relationship(back_populates="teacher")
    enrollments: _enrollment_cls = Relationship(back_populates="student")
