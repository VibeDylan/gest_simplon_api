"""
Schémas Pydantic pour Group et GroupMember.
"""
from typing import List, Optional


from pydantic import BaseModel, ConfigDict


class GroupCreate(BaseModel):
    """Création d'un groupe (session + nom, optionnellement liste d'étudiants)."""
    session_id: int
    name: str
    student_ids: Optional[List[int]] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class GroupRead(BaseModel):
    """Lecture d'un groupe (avec liste d'ids des membres)."""
    id: int
    session_id: int
    name: str
    student_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class GroupUpdate(BaseModel):
    """Mise à jour partielle."""
    name: Optional[str] = None
    student_ids: Optional[List[int]] = None

    model_config = ConfigDict(str_strip_whitespace=True)
