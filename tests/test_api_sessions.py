"""
Tests d'intégration pour les routes sessions (API v1).

CRUD sessions, listes par formation / formateur / dates, erreurs métier
(formation/formateur introuvable, utilisateur non formateur, dates invalides).
"""
import uuid
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

_session_day_offset = 0

RANDOM_DAY_BASE = hash(uuid.uuid4().hex) % 50000


def _next_session_start() -> datetime:
    """Retourne une date de début unique (évite conflits avec données existantes ou autres tests)."""
    global _session_day_offset
    _session_day_offset += 1
    return datetime(2025, 6, 1, 9, 0, 0) + timedelta(
        days=RANDOM_DAY_BASE + _session_day_offset
    )


def _make_trainer(client: TestClient) -> int:
    """Crée un utilisateur formateur et retourne son id."""
    email = f"trainer_{uuid.uuid4().hex}@test.com"
    r = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Trainer",
            "last_name": "User",
            "role": "trainer",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def _make_learner(client: TestClient) -> int:
    """Crée un utilisateur apprenant et retourne son id."""
    email = f"learner_{uuid.uuid4().hex}@test.com"
    r = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "first_name": "Learner",
            "last_name": "User",
            "role": "learner",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def _make_formation(client: TestClient) -> int:
    """Crée une formation et retourne son id."""
    title = f"Formation {uuid.uuid4().hex[:8]}"
    r = client.post(
        "/api/v1/formations",
        json={"title": title, "duration_hours": 40, "level": "0"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def _make_session_payload(
    formation_id: int, teacher_id: int, start_dt: datetime | None = None
):
    """Payload de session avec dates par défaut (start_dt unique si non fourni)."""
    if start_dt is None:
        start_dt = _next_session_start()
    end_dt = start_dt + timedelta(hours=8)
    return {
        "formation_id": formation_id,
        "teacher_id": teacher_id,
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "capacity_max": 10,
        "status": "scheduled",
    }


def test_create_session_ok(client: TestClient) -> None:
    """Création d'une session avec formation et formateur valides renvoie 201."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    payload = _make_session_payload(formation_id, teacher_id)

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["formation_id"] == formation_id
    assert data["teacher_id"] == teacher_id
    assert data["capacity_max"] == 10
    assert data["status"] == "scheduled"
    assert "id" in data


def test_create_session_formation_not_found(client: TestClient) -> None:
    """Création avec formation_id inexistant renvoie 404 FORMATION_NOT_FOUND."""
    teacher_id = _make_trainer(client)
    payload = _make_session_payload(999999, teacher_id)

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 404
    assert response.json()["code"] == "FORMATION_NOT_FOUND"


def test_create_session_teacher_not_found(client: TestClient) -> None:
    """Création avec teacher_id inexistant renvoie 404 TEACHER_NOT_FOUND."""
    formation_id = _make_formation(client)
    payload = _make_session_payload(formation_id, 999999)

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 404
    assert response.json()["code"] == "TEACHER_NOT_FOUND"


def test_create_session_user_not_trainer(client: TestClient) -> None:
    """Création avec un utilisateur qui n'est pas formateur renvoie 400 USER_NOT_TRAINER."""
    formation_id = _make_formation(client)
    learner_id = _make_learner(client)
    payload = _make_session_payload(formation_id, learner_id)

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "USER_NOT_TRAINER"


def test_create_session_start_date_after_end_date(client: TestClient) -> None:
    """Création avec start_date >= end_date renvoie 422 (validation)."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    start = datetime(2025, 6, 1, 9, 0, 0)
    end = datetime(2025, 6, 1, 8, 0, 0)

    response = client.post(
        "/api/v1/sessions",
        json={
            "formation_id": formation_id,
            "teacher_id": teacher_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "capacity_max": 10,
            "status": "scheduled",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_create_session_start_date_already_exists(client: TestClient) -> None:
    """Création avec une start_date déjà utilisée par une autre session renvoie 400."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    start_dt = datetime(2025, 7, 1, 9, 0, 0)
    payload = _make_session_payload(formation_id, teacher_id, start_dt)

    client.post("/api/v1/sessions", json=payload)
    payload2 = _make_session_payload(formation_id, teacher_id, start_dt)
    payload2["end_date"] = (start_dt + timedelta(hours=6)).isoformat()

    response = client.post("/api/v1/sessions", json=payload2)
    assert response.status_code == 400
    assert response.json()["code"] == "SESSION_START_DATE_ALREADY_EXISTS"


def test_create_session_end_date_already_exists(client: TestClient) -> None:
    """Création avec une end_date déjà utilisée par une autre session renvoie 400."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    start_dt = datetime(2025, 8, 1, 9, 0, 0)
    end_dt = start_dt + timedelta(hours=8)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id, start_dt))

    start_dt2 = datetime(2025, 8, 1, 10, 0, 0)
    response = client.post(
        "/api/v1/sessions",
        json={
            "formation_id": formation_id,
            "teacher_id": teacher_id,
            "start_date": start_dt2.isoformat(),
            "end_date": end_dt.isoformat(),
            "capacity_max": 5,
            "status": "scheduled",
        },
    )
    assert response.status_code == 400
    assert response.json()["code"] == "SESSION_END_DATE_ALREADY_EXISTS"


def test_list_sessions_ok(client: TestClient) -> None:
    """Liste des sessions renvoie 200 et contient les sessions créées."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))

    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_session_ok(client: TestClient) -> None:
    """Récupération d'une session par ID renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    create = client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))
    assert create.status_code == 201
    session_id = create.json()["id"]

    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_get_session_not_found(client: TestClient) -> None:
    """Récupération avec un ID inexistant renvoie 404 SESSION_NOT_FOUND."""
    response = client.get("/api/v1/sessions/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "SESSION_NOT_FOUND"


def test_list_sessions_by_formation_id(client: TestClient) -> None:
    """Liste des sessions par formation_id renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))

    response = client.get(f"/api/v1/sessions/formation/{formation_id}")
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) >= 1
    assert all(s["formation_id"] == formation_id for s in sessions)


def test_list_sessions_by_teacher_id(client: TestClient) -> None:
    """Liste des sessions par teacher_id renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    create = client.post(
        "/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id)
    )
    assert create.status_code == 201
    created_id = create.json()["id"]

    response = client.get(f"/api/v1/sessions/teacher/{teacher_id}")
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) >= 1, f"Expected at least 1 session for teacher {teacher_id}"
    assert all(s["teacher_id"] == teacher_id for s in sessions)
    ids = [s["id"] for s in sessions]
    assert created_id in ids


def test_get_session_by_formation_id_and_teacher_id(client: TestClient) -> None:
    """Récupération par formation_id et teacher_id renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))

    response = client.get(f"/api/v1/sessions/formation/{formation_id}/teacher/{teacher_id}")
    assert response.status_code == 200
    assert response.json()["formation_id"] == formation_id
    assert response.json()["teacher_id"] == teacher_id


def test_get_session_by_start_date(client: TestClient) -> None:
    """Récupération par date de début renvoie 200 avec la session correspondante."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    start_dt = datetime(2025, 9, 15, 9, 0, 0)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id, start_dt))

    response = client.get("/api/v1/sessions/start_date/2025-09-15T09:00:00")
    assert response.status_code == 200
    assert "2025-09-15" in response.json()["start_date"]


def test_get_session_by_start_date_invalid_format(client: TestClient) -> None:
    """Récupération par date avec format invalide renvoie 422."""
    response = client.get("/api/v1/sessions/start_date/not-a-date")
    assert response.status_code == 422


def test_get_session_by_end_date(client: TestClient) -> None:
    """Récupération par date de fin renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    start_dt = datetime(2025, 10, 1, 9, 0, 0)
    end_dt = start_dt + timedelta(hours=8)
    client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id, start_dt))

    response = client.get(f"/api/v1/sessions/end_date/{end_dt.isoformat()}")
    assert response.status_code == 200


def test_update_session_ok(client: TestClient) -> None:
    """Mise à jour partielle d'une session renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    create = client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))
    assert create.status_code == 201
    session_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"capacity_max": 20},
    )
    assert response.status_code == 200
    assert response.json()["capacity_max"] == 20


def test_update_session_not_found(client: TestClient) -> None:
    """Mise à jour avec un ID inexistant renvoie 404."""
    response = client.patch(
        "/api/v1/sessions/999999",
        json={"capacity_max": 5},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "SESSION_NOT_FOUND"


def test_delete_session_ok(client: TestClient) -> None:
    """Suppression d'une session renvoie 204 ; GET ensuite renvoie 404."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    create = client.post("/api/v1/sessions", json=_make_session_payload(formation_id, teacher_id))
    assert create.status_code == 201
    session_id = create.json()["id"]

    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


def test_delete_session_not_found(client: TestClient) -> None:
    """Suppression avec un ID inexistant renvoie 404 SESSION_NOT_FOUND."""
    response = client.delete("/api/v1/sessions/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "SESSION_NOT_FOUND"
