"""
Tests d'intégration pour les routes utilisateurs (API v1).

Vérifient la création, la liste, les erreurs de validation et les conflits (email déjà utilisé).
"""
import uuid

from fastapi.testclient import TestClient


def test_create_user_ok(client: TestClient) -> None:
    """Création d'un utilisateur avec email unique renvoie 201 et les champs attendus."""
    email = f"test_{uuid.uuid4()}@test.com"
    response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Test",
            "last_name": "Test",
            "password": "password123",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert response.json()["first_name"] == "Test"
    assert response.json()["last_name"] == "Test"
    assert response.json()["role"] == "admin"

def test_create_user_email_already_used(client: TestClient) -> None:
    """Création avec un email déjà utilisé renvoie 409 et le code EMAIL_ALREADY_USED."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "password": "password123",
            "role": "admin",
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_USED"
    assert response.json()["message"] == "This email is already used."

def test_create_user_invalid_role(client: TestClient) -> None:
    """Création avec un rôle invalide renvoie 422 et VALIDATION_ERROR."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "password": "password123",
            "role": "invalid",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["message"] == "Champ invalide ou manquant : role."

def test_create_user_first_name_too_short(client: TestClient) -> None:
    """Création avec first_name trop court renvoie 422 et détail sur first_name."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@test.com",
            "first_name": "T",
            "last_name": "Test",
            "password": "password123",
            "role": "admin",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Champ invalide ou manquant : first_name."
    assert any(d["field"] == "first_name" for d in body["details"])

def test_create_user_last_name_too_short(client: TestClient) -> None:
    """Création avec last_name trop court renvoie 422 et détail sur last_name."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "shortlast@test.com",
            "first_name": "Test",
            "last_name": "X",
            "password": "password123",
            "role": "learner",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert any(d["field"] == "last_name" for d in body["details"])


def test_create_user_invalid_email(client: TestClient) -> None:
    """Création avec email invalide renvoie 422."""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "not-an-email",
            "first_name": "Test",
            "last_name": "Test",
            "password": "password123",
            "role": "learner",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_list_users_ok(client: TestClient) -> None:
    """Liste des utilisateurs renvoie 200 et contient les utilisateurs créés."""
    email1 = f"list1_{uuid.uuid4()}@test.com"
    email2 = f"list2_{uuid.uuid4()}@test.com"

    client.post(
        "/api/v1/users",
        json={
            "email": email1,
            "first_name": "Test1",
            "last_name": "Test1",
            "password": "password123",
            "role": "admin",
        },
    )
    client.post(
        "/api/v1/users",
        json={
            "email": email2,
            "first_name": "Test2",
            "last_name": "Test2",
            "password": "password123",
            "role": "admin",
        },
    )
    response = client.get("/api/v1/users", params={"offset": 0, "limit": 100})
    assert response.status_code == 200
    users = response.json()
    emails = {u["email"] for u in users}
    offset = 0
    while len(users) == 100 and (email1 not in emails or email2 not in emails):
        offset += 100
        r = client.get("/api/v1/users", params={"offset": offset, "limit": 100})
        assert r.status_code == 200
        users = r.json()
        emails.update(u["email"] for u in users)
    assert email1 in emails, f"Expected {email1} in collected {len(emails)} users"
    assert email2 in emails


def test_get_user_ok(client: TestClient) -> None:
    """Récupération d'un utilisateur par ID renvoie 200 et les champs attendus."""
    email = f"get_{uuid.uuid4()}@test.com"
    create = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Jean",
            "last_name": "Dupont",
            "password": "password123",
            "role": "trainer",
        },
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == email
    assert data["first_name"] == "Jean"
    assert data["last_name"] == "Dupont"
    assert data["role"] == "trainer"
    assert "registered_at" in data
    assert "updated_at" in data


def test_get_user_not_found(client: TestClient) -> None:
    """Récupération avec un ID inexistant renvoie 404 et USER_NOT_FOUND."""
    response = client.get("/api/v1/users/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"


def test_update_user_ok(client: TestClient) -> None:
    """Mise à jour partielle d'un utilisateur renvoie 200 et les données mises à jour."""
    email = f"update_{uuid.uuid4()}@test.com"
    create = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Before",
            "last_name": "Name",
            "password": "password123",
            "role": "learner",
        },
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"first_name": "After"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "After"
    assert data["last_name"] == "Name"
    assert data["email"] == email


def test_update_user_not_found(client: TestClient) -> None:
    """Mise à jour avec un ID inexistant renvoie 404 et USER_NOT_FOUND."""
    response = client.patch(
        "/api/v1/users/999999",
        json={"first_name": "Test"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"


def test_update_user_email_already_used(client: TestClient) -> None:
    """Mise à jour avec un email déjà utilisé par un autre utilisateur renvoie 409."""
    email1 = f"update1_{uuid.uuid4()}@test.com"
    email2 = f"update2_{uuid.uuid4()}@test.com"
    client.post(
        "/api/v1/users",
        json={"email": email1, "first_name": "User", "last_name": "One", "password": "password123", "role": "learner"},
    )
    create2 = client.post(
        "/api/v1/users",
        json={"email": email2, "first_name": "User", "last_name": "Two", "password": "password123", "role": "learner"},
    )
    assert create2.status_code == 201
    user2_id = create2.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user2_id}",
        json={"email": email1},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_USED"


def test_delete_user_ok(client: TestClient) -> None:
    """Suppression d'un utilisateur par ID renvoie 204 ; GET ensuite renvoie 404."""
    email = f"del_{uuid.uuid4()}@test.com"
    create = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "To",
            "last_name": "Delete",
            "password": "password123",
            "role": "learner",
        },
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(client: TestClient) -> None:
    """Suppression avec un ID inexistant renvoie 404 et USER_NOT_FOUND."""
    response = client.delete("/api/v1/users/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"