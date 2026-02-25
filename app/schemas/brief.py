"""
Schémas Pydantic pour l'entité Brief.

DTOs de validation entrée (création, mise à jour) et sortie (lecture).
Un brief peut être assigné à plusieurs étudiants (student_ids) ou à un groupe (group_id).
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BriefCreate(BaseModel):
    """
    Payload de création d'un brief.

    Assignation : soit student_ids (liste d'ids), soit group_id (les membres du groupe seront assignés).
    Si les deux sont fournis, group_id est prioritaire. Les deux optionnels = brief sans assignés.
    """
    title: str
    description: Optional[str] = None
    delivery_deadline: datetime
    order: int = 0
    session_id: int
    student_ids: Optional[List[int]] = None
    group_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class BriefRead(BaseModel):
    """Représentation en lecture d'un brief (avec liste d'ids étudiants)."""
    id: int
    title: str
    description: Optional[str] = None
    delivery_deadline: datetime
    order: int
    session_id: int
    student_ids: List[int] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BriefUpdate(BaseModel):
    """Payload de mise à jour partielle (tous les champs optionnels)."""
    title: Optional[str] = None
    description: Optional[str] = None
    delivery_deadline: Optional[datetime] = None
    order: Optional[int] = None
    session_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    group_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True)
