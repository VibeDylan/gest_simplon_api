"""
Tests d'intégration pour les routes inscriptions (API v1).

CRUD enrollments, listes par session / étudiant, erreurs métier
(session/user introuvable, inscription déjà existante, session pleine).
"""
import uuid
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

_session_day_offset = 0

RANDOM_DAY_BASE = 60000 + (hash(uuid.uuid4().hex) % 10000)


def _next_session_start() -> datetime:
    """Retourne une date de début unique (évite conflit avec test_api_sessions)."""
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
            "password": "password123",
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
            "password": "password123",
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


def _make_session(
    client: TestClient,
    formation_id: int,
    teacher_id: int,
    capacity_max: int = 10,
    start_dt: datetime | None = None,
) -> int:
    """Crée une session et retourne son id (start_dt unique si non fourni)."""
    if start_dt is None:
        start_dt = _next_session_start()
    end_dt = start_dt + timedelta(hours=8)
    r = client.post(
        "/api/v1/sessions",
        json={
            "formation_id": formation_id,
            "teacher_id": teacher_id,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "capacity_max": capacity_max,
            "status": "scheduled",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_create_enrollment_ok(client: TestClient) -> None:
    """Création d'une inscription avec session et étudiant valides renvoie 201."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)

    response = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == session_id
    assert data["student_id"] == student_id
    assert "id" in data
    assert "enrolled_at" in data


def test_create_enrollment_session_not_found(client: TestClient) -> None:
    """Création avec session_id inexistant renvoie 404 SESSION_NOT_FOUND."""
    student_id = _make_learner(client)

    response = client.post(
        "/api/v1/enrollments",
        json={"session_id": 999999, "student_id": student_id},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "SESSION_NOT_FOUND"


def test_create_enrollment_user_not_found(client: TestClient) -> None:
    """Création avec student_id inexistant renvoie 404 USER_NOT_FOUND."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)

    response = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": 999999},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"


def test_create_enrollment_already_exists(client: TestClient) -> None:
    """Création avec (session_id, student_id) déjà inscrit renvoie 409 ENROLLMENT_ALREADY_EXISTS."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)

    client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    response = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "ENROLLMENT_ALREADY_EXISTS"


def test_create_enrollment_session_full(client: TestClient) -> None:
    """Création quand la session est pleine renvoie 400 ENROLLMENT_SESSION_FULL."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id, capacity_max=2)
    student1 = _make_learner(client)
    student2 = _make_learner(client)
    student3 = _make_learner(client)

    client.post("/api/v1/enrollments", json={"session_id": session_id, "student_id": student1})
    client.post("/api/v1/enrollments", json={"session_id": session_id, "student_id": student2})

    response = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student3},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "ENROLLMENT_SESSION_FULL"


def test_list_enrollments_ok(client: TestClient) -> None:
    """Liste des inscriptions renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    client.post("/api/v1/enrollments", json={"session_id": session_id, "student_id": student_id})

    response = client.get("/api/v1/enrollments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_enrollment_ok(client: TestClient) -> None:
    """Récupération d'une inscription par ID renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    create = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    assert create.status_code == 201
    enrollment_id = create.json()["id"]

    response = client.get(f"/api/v1/enrollments/{enrollment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == enrollment_id


def test_get_enrollment_not_found(client: TestClient) -> None:
    """Récupération avec un ID inexistant renvoie 404 ENROLLMENT_NOT_FOUND."""
    response = client.get("/api/v1/enrollments/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "ENROLLMENT_NOT_FOUND"


def test_list_enrollments_by_session_id(client: TestClient) -> None:
    """Liste des inscriptions par session_id renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    client.post("/api/v1/enrollments", json={"session_id": session_id, "student_id": student_id})

    response = client.get(f"/api/v1/enrollments/session/{session_id}")
    assert response.status_code == 200
    enrollments = response.json()
    assert len(enrollments) >= 1
    assert all(e["session_id"] == session_id for e in enrollments)


def test_list_enrollments_by_student_id(client: TestClient) -> None:
    """Liste des inscriptions par student_id renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    client.post("/api/v1/enrollments", json={"session_id": session_id, "student_id": student_id})

    response = client.get(f"/api/v1/enrollments/student/{student_id}")
    assert response.status_code == 200
    enrollments = response.json()
    assert len(enrollments) >= 1
    assert all(e["student_id"] == student_id for e in enrollments)


def test_update_enrollment_ok(client: TestClient) -> None:
    """Mise à jour partielle d'une inscription renvoie 200."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    create = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    assert create.status_code == 201
    enrollment_id = create.json()["id"]

    student2_id = _make_learner(client)
    response = client.patch(
        f"/api/v1/enrollments/{enrollment_id}",
        json={"student_id": student2_id},
    )
    assert response.status_code == 200
    assert response.json()["student_id"] == student2_id


def test_update_enrollment_not_found(client: TestClient) -> None:
    """Mise à jour avec un ID inexistant renvoie 404."""
    response = client.patch(
        "/api/v1/enrollments/999999",
        json={"student_id": 1},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "ENROLLMENT_NOT_FOUND"


def test_delete_enrollment_ok(client: TestClient) -> None:
    """Suppression d'une inscription renvoie 204 ; GET ensuite renvoie 404."""
    formation_id = _make_formation(client)
    teacher_id = _make_trainer(client)
    session_id = _make_session(client, formation_id, teacher_id)
    student_id = _make_learner(client)
    create = client.post(
        "/api/v1/enrollments",
        json={"session_id": session_id, "student_id": student_id},
    )
    assert create.status_code == 201
    enrollment_id = create.json()["id"]

    response = client.delete(f"/api/v1/enrollments/{enrollment_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/enrollments/{enrollment_id}")
    assert get_response.status_code == 404


def test_delete_enrollment_not_found(client: TestClient) -> None:
    """Suppression avec un ID inexistant renvoie 404 ENROLLMENT_NOT_FOUND."""
    response = client.delete("/api/v1/enrollments/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "ENROLLMENT_NOT_FOUND"
