"""
Schémas Pydantic pour l'entité Session.

DTOs de validation entrée (création, mise à jour) et sortie (lecture).
Contrôle de l'ordre des dates (start_date < end_date) dans les validateurs.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.utils.enum import SessionStatus


class SessionCreate(BaseModel):
    """
    Payload de création d'une session.

    formation_id: ID de la formation.
    teacher_id: ID du formateur.
    start_date: Date de début.
    end_date: Date de fin.
    capacity_max: Capacité maximale (≥ 1).
    status: SessionStatus.
    """
    formation_id: int
    teacher_id: int
    start_date: datetime
    end_date: datetime
    capacity_max: int
    status: SessionStatus

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_dates_order(self) -> "SessionCreate":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self

    def model_post_init(self, __context: Any) -> None:
        self.capacity_max = max(1, int(self.capacity_max))
        self.status = SessionStatus(self.status)

class SessionUpdate(BaseModel):
    """
    Payload de mise à jour partielle d'une session.

    formation_id: ID de la formation.
    teacher_id: ID du formateur.
    start_date: Date de début.
    end_date: Date de fin.
    capacity_max: Capacité maximale (≥ 1).
    status: SessionStatus.
    """
    formation_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    capacity_max: Optional[int] = None
    status: Optional[SessionStatus] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_dates_order(self) -> "SessionUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.start_date >= self.end_date:
                raise ValueError("start_date must be before end_date")
        return self

    def model_post_init(self, __context: Any) -> None:
        if self.capacity_max is not None:
            self.capacity_max = max(1, int(self.capacity_max))
        if self.status is not None:
            self.status = SessionStatus(self.status)


class SessionRead(BaseModel):
    """
    Représentation en lecture d'une session (sortie API).

    Sérialisable depuis le modèle ORM (from_attributes=True).
    """
    id: int
    formation_id: int
    teacher_id: int
    start_date: datetime
    end_date: datetime
    capacity_max: int
    status: SessionStatus

    model_config = ConfigDict(from_attributes=True)