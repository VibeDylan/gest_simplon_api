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
        test_database_url: URL de la base de test (optionnelle).
        env: Environnement d'exécution (dev, prod, etc.), défaut "dev".
    """

    database_url: str = Field(..., env="DATABASE_URL")
    test_database_url: str | None = Field(default=None, env="TEST_DATABASE_URL")
    env: str = Field(default="dev", env="ENV")

    class Config:
        """Configuration Pydantic : chargement depuis .env, ignore les champs extra."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()