"""
Configuration centralisée de l'application.

Charge les variables d'environnement depuis `.env` (pydantic-settings)
et expose un singleton `settings` pour DATABASE_URL, ENV, etc.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Paramètres de l'application chargés depuis l'environnement.

    Attributes:
        database_url: URL de connexion PostgreSQL (obligatoire).
        env: Environnement d'exécution (dev, prod, etc.), défaut "dev".
    """

    database_url: str = Field(..., env="DATABASE_URL")
    env: str = Field(default="dev", env="ENV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings() 