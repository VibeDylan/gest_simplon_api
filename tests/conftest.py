"""
Configuration des tests (pytest).

Active la base de test via USE_TEST_DB=1 avant l'import de l'app, et fournit
la fixture `client` (TestClient FastAPI) pour les tests d'API.
"""
import os

import pytest
from fastapi.testclient import TestClient

os.environ["USE_TEST_DB"] = "1"
from main import app


@pytest.fixture
def client() -> TestClient:
    """Client HTTP de test pour l'API FastAPI (injection dans les tests)."""
    return TestClient(app)