"""
Schémas Pydantic pour l'entité User.

DTOs de validation entrée (création, mise à jour) et sortie (lecture).
Les emails sont normalisés en minuscules à la validation.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator, field_validator

from app.utils.enum import Role


class UserCreate(BaseModel):
    """
    Payload de création d'un utilisateur.

    email normalisé en minuscules. role par défaut : LEARNER.
    """

    email: EmailStr
    first_name: str
    last_name: str
    role: Role = Role.LEARNER

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("first_name")
    @classmethod
    def first_name_min_length(cls, v: str) -> str:
        if len((v or "").strip()) < 2:
            raise ValueError("first_name must have at least 2 characters")
        return v

    @field_validator("last_name")
    @classmethod
    def last_name_min_length(cls, v: str) -> str:
        if len((v or "").strip()) < 2:
            raise ValueError("last_name must have at least 2 characters")
        return v

    def model_post_init(self, __context: Any) -> None:
        self.email = self.email.lower()


class UserUpdate(BaseModel):
    """
    Payload de mise à jour partielle (tous les champs optionnels).

    Seuls les champs fournis sont mis à jour. email normalisé en minuscules si présent.
    """

    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[Role] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("first_name")
    @classmethod
    def first_name_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 2:
            raise ValueError("first_name must have at least 2 characters")
        return v

    @field_validator("last_name")
    @classmethod
    def last_name_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 2:
            raise ValueError("last_name must have at least 2 characters")
        return v

    def model_post_init(self, __context: Any) -> None:
        if self.email is not None:
            self.email = self.email.lower()


class UserRead(BaseModel):
    """
    Représentation en lecture d'un utilisateur (sortie API).

    Sérialisable depuis le modèle ORM (from_attributes=True).
    """

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: Role
    registered_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)