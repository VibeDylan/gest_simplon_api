"""
Session de base de données SQLModel.

Crée le moteur à partir de `settings.database_url` et, en contexte tests,
de `settings.test_database_url` si disponible. Fournit un générateur
`get_session()` pour l'injection de dépendances FastAPI.
"""
import os

from sqlmodel import Session, create_engine

from app.core.config import settings


def _get_engine_url() -> str:
    """
    Retourne l'URL de base de données à utiliser.

    - En temps normal : `settings.database_url`.
    - Pendant les tests (env USE_TEST_DB=1) : `settings.test_database_url` si définie,
      sinon on retombe sur `database_url`.
    """
    use_test_db = os.getenv("USE_TEST_DB") == "1"
    if use_test_db and settings.test_database_url:
        return settings.test_database_url
    return settings.database_url


_ENGINE_URL = _get_engine_url()

# Info simple pour vérifier facilement l'URL utilisée (utile surtout en tests).
print(f"[DB] Using engine URL: {_ENGINE_URL}")

engine = create_engine(_ENGINE_URL)


def get_session():
    """
    Générateur de session SQLModel (context manager).

    À utiliser comme dépendance FastAPI : Depends(get_session).
    Ferme automatiquement la session après la requête.
    """
    with Session(engine) as session:
        yield session
