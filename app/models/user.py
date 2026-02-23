"""
Modèle utilisateur (table `users`).

Représente un utilisateur du système : admin, formateur (trainer) ou apprenant (learner).
Lié aux sessions qu'il anime (taught_sessions) et aux inscriptions (enrollments).
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship
from app.utils.enum import Role

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.session import Session


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
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    role: Role = Field(default=Role.LEARNER)

    taught_sessions: list["Session"] = Relationship(back_populates="teacher")
    enrollments: list["Enrollment"] = Relationship(back_populates="student")
