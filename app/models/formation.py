"""
Modèle formation (table `formations`).

Définit un parcours de formation avec niveau et durée.
Une formation peut avoir plusieurs sessions.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import Session


class Level(str, Enum):
    """Niveau de la formation : débutant, intermédiaire, avancé."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Formation(SQLModel, table=True):
    """
    Formation (parcours pédagogique).

    Attributes:
        id: Clé primaire.
        title: Titre (min 2 caractères).
        description: Description optionnelle.
        duration_hours: Durée en heures (strictement positive).
        level: Niveau (beginner, intermediate, advanced).
        created_at, updated_at: Horodatages.
        sessions: Liste des sessions associées.
    """

    __tablename__ = "formations"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=2)
    description: Optional[str] = Field(default=None)
    duration_hours: int = Field(gt=0)
    level: Level = Field(default=Level.BEGINNER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    sessions: list["Session"] = Relationship(back_populates="formation")
