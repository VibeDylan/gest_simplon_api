"""
Schémas Pydantic pour l'authentification.

DTOs de validation entrée (connexion, changement de mot de passe) et sortie (réponse).
"""
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: str) -> str:
        if len((v or "")) < 8:
            raise ValueError("new_password must have at least 8 characters")
        return v