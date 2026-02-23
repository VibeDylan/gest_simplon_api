from pydantic import BaseModel
from typing import Optional
from app.utils.enum import Level
from pydantic import ConfigDict
from typing import Any
from datetime import datetime


class FormationCreate(BaseModel):
    """
    Payload de création d'une formation.

    title: Titre (min 2 caractères).
    description: Description optionnelle.
    duration_hours: Durée en heures (strictement positive).
    level: Niveau (beginner, intermediate, advanced).
    """
    title: str
    description: Optional[str] = None
    duration_hours: int
    level: Level

    model_config = ConfigDict(str_strip_whitespace=True)
    def model_post_init(self, __context: Any):
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
    def model_post_init(self, __context: Any):
        if self.title:
            self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        if self.duration_hours:
            self.duration_hours = max(1, int(self.duration_hours))
        if self.level:
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
