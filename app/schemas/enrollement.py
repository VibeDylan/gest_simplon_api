from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    """
    Payload de création d'une inscription.

    session_id: ID de la session.
    student_id: ID de l'étudiant.
    """
    session_id: int
    student_id: int

    model_config = ConfigDict(str_strip_whitespace=True)

class EnrollmentRead(BaseModel):
    """
    Représentation en lecture d'une inscription.

    Sérialisable depuis le modèle ORM (from_attributes=True).
    """
    id: int
    session_id: int
    student_id: int
    enrolled_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EnrollmentUpdate(BaseModel):
    """
    Payload de mise à jour partielle d'une inscription.

    session_id: ID de la session.
    student_id: ID de l'étudiant.
    """
    session_id: Optional[int] = None
    student_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True)