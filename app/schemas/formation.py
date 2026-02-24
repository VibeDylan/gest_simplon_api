from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.utils.enum import Level

MAX_DURATION_HOURS = 10_000


class FormationCreate(BaseModel):
    """
    Payload de création d'une formation.

    title: Titre (min 2 caractères).
    description: Description optionnelle.
    duration_hours: Durée en heures (strictement positive).
    level: Niveau (0 = BEGINNER, 1 = INTERMEDIATE, 2 = ADVANCED).
    """
    title: str
    description: Optional[str] = None
    duration_hours: int
    level: Level

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_title_and_duration(self) -> "FormationCreate":
        if len((self.title or "").strip()) < 2:
            raise ValueError("title must have at least 2 characters")
        if not (1 <= self.duration_hours <= MAX_DURATION_HOURS):
            raise ValueError(f"duration_hours must be between 1 and {MAX_DURATION_HOURS}")
        return self

    def model_post_init(self, __context: Any) -> None:
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else None
        self.duration_hours = max(1, int(self.duration_hours))
        self.level = Level(self.level)


class FormationUpdate(BaseModel):
    """
    Payload de mise à jour partielle d'une formation.

    title: Titre (min 2 caractères).
    description: Description optionnelle.
    duration_hours: Durée en heures (strictement positive).
    level: Niveau (beginner, intermediate, advanced).
    """
    title: Optional[str] = None
    description: Optional[str] = None
    duration_hours: Optional[int] = None
    level: Optional[Level] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_title_and_duration(self) -> "FormationUpdate":
        if self.title is not None and len(self.title.strip()) < 2:
            raise ValueError("title must have at least 2 characters")
        if self.duration_hours is not None and not (1 <= self.duration_hours <= MAX_DURATION_HOURS):
            raise ValueError(f"duration_hours must be between 1 and {MAX_DURATION_HOURS}")
        return self

    def model_post_init(self, __context: Any) -> None:
        if self.title is not None:
            self.title = self.title.strip()
        if self.description is not None:
            self.description = self.description.strip()
        if self.duration_hours is not None:
            self.duration_hours = max(1, int(self.duration_hours))
        if self.level is not None:
            self.level = Level(self.level)


class FormationRead(BaseModel):
    """
    Représentation en lecture d'une formation (sortie API).

    Sérialisable depuis le modèle ORM (from_attributes=True).
    """
    id: int
    title: str
    description: Optional[str] = None
    duration_hours: int
    level: Level
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
