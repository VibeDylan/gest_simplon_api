"""
Modèle brief (table `briefs`).

Table d'association entre Session et User (apprenant).
Contrainte unique (session_id, student_id) : un brief par session et par apprenant.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from app.models.session import Session
from app.models.user import User


class Brief(SQLModel, table=True):
    """
    Brief (devoir) d'une session.

    Attributes:
        id: Clé primaire.
        title: Titre (min 2 caractères, max 255 caractères).
        descritpion: Description optionnelle.
        delivery_deadline: Date de livraison.
        order: Ordre du devoir.
        session_id: Clé étrangère vers Session.
        student_id: Clé étrangère vers User.
        created_at: Horodatage de création.
        updated_at: Horodatage de mise à jour.
        session: Relation vers Session.
        student: Relation vers User.
    """
    __tablename__ = "briefs"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_brief_session_student"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=2, max_length=255)
    descritpion: Optional[str] = Field(default=None)
    delivery_deadline: datetime
    order: int
    session_id: int = Field(foreign_key="sessions.id")
    student_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    session: Session = Relationship(back_populates="briefs")
    student: User = Relationship(back_populates="briefs")