"""
Schémas Pydantic pour l'entité Brief.

DTOs de validation entrée (création, mise à jour) et sortie (lecture).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class BriefCreate(BaseModel):
    """
    Payload de création d'un brief.

    title: Titre (min 2 caractères, max 255 caractères).
    descritpion: Description optionnelle.
    delivery_deadline: Date de livraison.
    order: Ordre du devoir.
    session_id: Clé étrangère vers Session.
    student_id: Clé étrangère vers User.
    """
    title: str
    descritpion: Optional[str] = None
    delivery_deadline: datetime
    order: int
    session_id: int
    student_id: int

    model_config = ConfigDict(str_strip_whitespace=True)

class BriefRead(BaseModel):
    """
    Représentation en lecture d'un brief.

    Sérialisable depuis le modèle ORM (from_attributes=True).
    """
    id: int
    title: str
    descritpion: Optional[str] = None
    delivery_deadline: datetime
    order: int
    session_id: int
    student_id: int

    model_config = ConfigDict(from_attributes=True)

class BriefUpdate(BaseModel):
    """
    Payload de mise à jour partielle d'un brief.

    title: Titre (min 2 caractères, max 255 caractères).
    descritpion: Description optionnelle.
    delivery_deadline: Date de livraison.
    order: Ordre du devoir.
    session_id: Clé étrangère vers Session.
    student_id: Clé étrangère vers User.
    """
    title: Optional[str] = None
    descritpion: Optional[str] = None
    delivery_deadline: Optional[datetime] = None
    order: Optional[int] = None
    session_id: Optional[int] = None
    student_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    