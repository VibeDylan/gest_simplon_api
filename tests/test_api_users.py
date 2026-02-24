from fastapi import responses
from fastapi.testclient import TestClient
import uuid


def test_create_user_ok(client: TestClient) -> None:
    email = f"test_{uuid.uuid4()}@test.com"
    response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Test",
            "last_name": "Test",
            "role": "admin",
        },
    )


    assert response.status_code == 201
    assert response.json()["email"] == email
    assert response.json()["first_name"] == "Test"
    assert response.json()["last_name"] == "Test"
    assert response.json()["role"] == "admin"

def test_create_user_email_already_used(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "role": "admin",
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_USED"
    assert response.json()["message"] == "This email is already used."

def test_create_user_invalid_role(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "role": "invalid",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["message"] == "Champ invalide ou manquant : role."