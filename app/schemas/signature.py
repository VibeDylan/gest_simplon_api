"""
Schémas Pydantic pour l'émargement (signature).

Création (session_id, user_id, date optionnelle = aujourd'hui) et lecture.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SignatureCreate(BaseModel):
    """
    Payload pour émarger (une signature = un jour signé).

    session_id: Session de formation.
    user_id: Apprenant qui signe.
    date: Jour d'émargement (optionnel, défaut = aujourd'hui).
    """
    session_id: int
    user_id: int
    date: Optional[date] = None 

    model_config = ConfigDict(str_strip_whitespace=True)


class SignatureRead(BaseModel):
    """Représentation en lecture d'une signature (sortie API)."""
    id: int
    session_id: int
    user_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
