import pytest
from fastapi.testclient import TestClient
from main import app
from typing import Any

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)