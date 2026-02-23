"""
Session de base de données SQLModel.

Crée le moteur à partir de `settings.database_url` et fournit
un générateur `get_session()` pour l'injection de dépendances FastAPI.
"""
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url)


def get_session():
    """
    Générateur de session SQLModel (context manager).

    À utiliser comme dépendance FastAPI : Depends(get_session).
    Ferme automatiquement la session après la requête.
    """
    with Session(engine) as session:
        yield session
