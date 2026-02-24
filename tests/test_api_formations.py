"""
Tests d'intégration pour les routes formations (API v1).

CRUD formations, validation (titre, durée, niveau), conflits (titre déjà utilisé).
"""
import uuid

from fastapi.testclient import TestClient


def test_create_formation_ok(client: TestClient) -> None:
    """Création d'une formation avec champs valides renvoie 201 et les champs attendus."""
    title = f"Formation {uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/formations",
        json={
            "title": title,
            "description": "Description test",
            "duration_hours": 40,
            "level": "1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == title
    assert data["description"] == "Description test"
    assert data["duration_hours"] == 40
    assert data["level"] == "1"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_formation_title_already_used(client: TestClient) -> None:
    """Création avec un titre déjà existant renvoie 409 et FORMATION_TITLE_ALREADY_USED."""
    title = f"Unique {uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 10, "level": "0"},
    )
    response = client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 20, "level": "0"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "FORMATION_TITLE_ALREADY_USED"
    assert "title" in response.json()["message"].lower() or "formation" in response.json()["message"].lower()


def test_create_formation_title_too_short(client: TestClient) -> None:
    """Création avec un titre de moins de 2 caractères renvoie 422."""
    response = client.post(
        "/api/v1/formations",
        json={"title": "A", "duration_hours": 10, "level": "0"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_create_formation_duration_invalid(client: TestClient) -> None:
    """Création avec duration_hours hors limites (> 10_000) renvoie 422."""
    response = client.post(
        "/api/v1/formations",
        json={"title": "Valid Title", "duration_hours": 10001, "level": "0"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_create_formation_invalid_level(client: TestClient) -> None:
    """Création avec un niveau invalide renvoie 422."""
    response = client.post(
        "/api/v1/formations",
        json={"title": "Valid Title", "duration_hours": 10, "level": "99"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_list_formations_ok(client: TestClient) -> None:
    """Liste des formations renvoie 200 et contient les formations créées."""
    title = f"List {uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 10, "level": "0"},
    )
    titles = []
    offset = 0
    while True:
        response = client.get("/api/v1/formations", params={"offset": offset, "limit": 100})
        assert response.status_code == 200
        formations = response.json()
        titles.extend(f["title"] for f in formations)
        if len(formations) < 100:
            break
        offset += 100
    assert title in titles, f"Expected {title} in {len(titles)} formations"


def test_get_formation_ok(client: TestClient) -> None:
    """Récupération d'une formation par ID renvoie 200 et les champs attendus."""
    title = f"Get {uuid.uuid4().hex[:8]}"
    create = client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 25, "level": "2"},
    )
    assert create.status_code == 201
    formation_id = create.json()["id"]

    response = client.get(f"/api/v1/formations/{formation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == formation_id
    assert data["title"] == title
    assert data["duration_hours"] == 25
    assert data["level"] == "2"


def test_get_formation_not_found(client: TestClient) -> None:
    """Récupération avec un ID inexistant renvoie 404 et FORMATION_NOT_FOUND."""
    response = client.get("/api/v1/formations/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "FORMATION_NOT_FOUND"


def test_update_formation_ok(client: TestClient) -> None:
    """Mise à jour partielle d'une formation renvoie 200 et les données mises à jour."""
    title = f"Update {uuid.uuid4().hex[:8]}"
    new_title = f"Updated {uuid.uuid4().hex[:8]}"
    create = client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 10, "level": "0"},
    )
    assert create.status_code == 201
    formation_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/formations/{formation_id}",
        json={"title": new_title},
    )
    assert response.status_code == 200
    assert response.json()["title"] == new_title
    assert response.json()["duration_hours"] == 10


def test_update_formation_not_found(client: TestClient) -> None:
    """Mise à jour avec un ID inexistant renvoie 404."""
    response = client.patch(
        "/api/v1/formations/999999",
        json={"title": "New Title"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "FORMATION_NOT_FOUND"


def test_update_formation_title_already_used(client: TestClient) -> None:
    """Mise à jour avec un titre déjà pris par une autre formation renvoie 409."""
    t1 = f"First {uuid.uuid4().hex[:8]}"
    t2 = f"Second {uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/formations",
        json={"title": t1, "duration_hours": 10, "level": "0"},
    )
    create2 = client.post(
        "/api/v1/formations",
        json={"title": t2, "duration_hours": 20, "level": "1"},
    )
    assert create2.status_code == 201
    formation2_id = create2.json()["id"]

    response = client.patch(
        f"/api/v1/formations/{formation2_id}",
        json={"title": t1},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "FORMATION_TITLE_ALREADY_USED"


def test_delete_formation_ok(client: TestClient) -> None:
    """Suppression d'une formation renvoie 204 ; GET ensuite renvoie 404."""
    title = f"Del {uuid.uuid4().hex[:8]}"
    create = client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 10, "level": "0"},
    )
    assert create.status_code == 201
    formation_id = create.json()["id"]

    response = client.delete(f"/api/v1/formations/{formation_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/formations/{formation_id}")
    assert get_response.status_code == 404


def test_delete_formation_not_found(client: TestClient) -> None:
    """Suppression avec un ID inexistant renvoie 404 et FORMATION_NOT_FOUND."""
    response = client.delete("/api/v1/formations/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "FORMATION_NOT_FOUND"
