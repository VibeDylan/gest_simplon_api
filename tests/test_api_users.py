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

def test_create_user_first_name_too_short(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "T",  
            "last_name": "Test",
            "role": "admin",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Champ invalide ou manquant : first_name."
    assert any(d["field"] == "first_name" for d in body["details"])

def test_list_users_ok(client: TestClient) -> None:
    email1 = f"list1_{uuid.uuid4()}@test.com"
    email2 = f"list2_{uuid.uuid4()}@test.com"

    client.post(
        "/api/v1/users",
        json={
            "email": email1,
            "first_name": "Test1",
            "last_name": "Test1",
            "role": "admin",
        },
    )
    client.post(
        "/api/v1/users",
        json={
            "email": email2,
            "first_name": "Test2",
            "last_name": "Test2",
            "role": "admin",
        },
    )
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()

    emails = {u["email"] for u in users}
    assert email1 in emails
    assert email2 in emails