# GestSimplon API

API REST pour la gestion d’un centre de formation : **utilisateurs** (administrateurs, formateurs, apprenants), **formations**, **sessions** et **inscriptions**. Conçue avec FastAPI, Pydantic v2, SQLModel et PostgreSQL.

---

## Sommaire

- [Contexte et objectifs](#contexte-et-objectifs)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancer le projet](#lancer-le-projet)
- [Documentation de l’API](#documentation-de-lapi)
- [Structure du projet](#structure-du-projet)
- [Modèles et relations](#modèles-et-relations)
- [Migrations (Alembic)](#migrations-alembic)
- [Tests automatisés](#tests-automatisés)
- [Gestion des erreurs](#gestion-des-erreurs)

---

## Contexte et objectifs

Cette API permet de :

- **Utilisateurs** : CRUD avec rôles (admin, formateur, apprenant), email unique, date d’inscription.
- **Formations** : CRUD avec titre, description, durée (heures), niveau (débutant, intermédiaire, avancé).
- **Sessions** : CRUD avec formation, formateur, dates de début/fin, capacité maximale, statut (planifiée, en cours, terminée).
- **Inscriptions** : inscrire un apprenant à une session, lister les inscrits d’une session, lister les inscriptions d’un apprenant, désinscrire.

Contraintes métier assurées côté API : email unique, dates cohérentes (début &lt; fin), capacité non dépassée, une inscription par (session, apprenant), formateur obligatoirement de rôle « formateur ».

---

## Stack technique

| Composant        | Technologie                          |
|------------------|--------------------------------------|
| Framework API    | FastAPI                              |
| Validation / DTOs| Pydantic v2                          |
| ORM / Base       | SQLModel, PostgreSQL (psycopg2)      |
| Migrations       | Alembic                              |
| Tests            | pytest, pytest-cov                   |
| Serveur          | Uvicorn                              |

---

## Prérequis

- **Python 3.11+**
- **PostgreSQL** (ou Docker pour lancer Postgres en conteneur)
- **pip** et **venv**

---

## Installation

```bash
# Cloner le dépôt
git clone <url_du_repo>
cd gestsimplon

# Environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux / macOS
# ou : venv\Scripts\activate   # Windows

# Dépendances
pip install -r requirements.txt
```

---

## Configuration

### Variables d’environnement

Copier `.env.example` vers `.env` et adapter les valeurs :

```bash
cp .env.example .env
```

| Variable             | Description                         | Exemple |
|----------------------|-------------------------------------|--------|
| `POSTGRES_USER`      | Utilisateur PostgreSQL              | `postgres` |
| `POSTGRES_PASSWORD`  | Mot de passe PostgreSQL             | `postgres` |
| `POSTGRES_DB`        | Nom de la base principale           | `gestsimplon` |
| `DATABASE_URL`       | URL de connexion (base principale)   | `postgresql://postgres:postgres@localhost:5444/gestsimplon` |
| `TEST_DATABASE_URL`  | URL de la base de test (pour pytest)| `postgresql://postgres:postgres@localhost:5444/gestsimplon_test` |
| `ENV`                | Environnement (optionnel)           | `dev` (défaut) |
| `SECRET_KEY`                | JWT Token Secret Key        |  |


- Le port **5444** correspond au mapping Docker (`5444:5432`). Si Postgres est en local sur 5432, adapter les URLs.
- Pour exécuter les tests, définir `TEST_DATABASE_URL` sur une base dédiée (ex. `gestsimplon_test`). Les tests activent automatiquement cette base via la variable interne `USE_TEST_DB`.

### Base de données avec Docker

```bash
docker compose up -d
```

- Postgres est exposé sur le port **5444**.
- Le script `docker/initdb/01-create-test-db.sql` crée la base `gestsimplon_test` au premier démarrage (pour les tests).
- Données persistées dans le volume `postgres_data`.

---

## Lancer le projet

```bash
# À la racine du projet (avec l’environnement virtuel activé)
uvicorn main:app --reload
```

- **API** : http://127.0.0.1:8000  
- **Swagger (OpenAPI)** : http://127.0.0.1:8000/docs  
- **ReDoc** : http://127.0.0.1:8000/redoc  

Penser à appliquer les migrations avant le premier lancement : `alembic upgrade head`.

---

## Documentation de l’API

La documentation interactive est générée par FastAPI :

- **Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — essai des endpoints, schémas des requêtes/réponses.
- **ReDoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) — lecture structurée de l’API.

### Préfixe et ressources

| Préfixe        | Ressource    | Principaux endpoints |
|----------------|-------------|-----------------------|
| `/api/v1/users`       | Utilisateurs   | `POST` création, `GET` liste (pagination), `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` |
| `/api/v1/formations`  | Formations     | `POST`, `GET` (pagination), `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` |
| `/api/v1/sessions`    | Sessions       | `POST`, `GET`, `GET /{id}`, `GET /formation/{id}`, `GET /teacher/{id}`, `GET /start_date/...`, `GET /end_date/...`, `PATCH /{id}`, `DELETE /{id}` |
| `/api/v1/enrollments` | Inscriptions   | `POST`, `GET`, `GET /{id}`, `GET /session/{session_id}`, `GET /student/{student_id}`, `PATCH /{id}`, `DELETE /{id}` |

- **Pagination** : paramètres de requête `offset` et `limit` (ex. `GET /api/v1/users?offset=0&limit=100`).
- **Dates** : format ISO 8601 en JSON (ex. `"2025-10-12T09:00:00"` pour les sessions).
- **Niveau formation** : valeurs `"0"` (débutant), `"1"` (intermédiaire), `"2"` (avancé).
- **Statut session** : `scheduled`, `ongoing`, `completed`.

---

## Structure du projet

```
gestsimplon/
├── main.py                    # Point d’entrée FastAPI, handlers d’erreurs
├── requirements.txt           # Dépendances Python
├── docker-compose.yml         # Service Postgres
├── alembic.ini
├── .env.example / .env
│
├── app/
│   ├── core/
│   │   ├── config.py          # Settings (pydantic-settings)
│   │   └── errors.py           # Exceptions métier (codes + messages)
│   ├── db/
│   │   ├── base.py            # Metadata Alembic, imports des modèles
│   │   └── session.py         # Moteur SQLModel, get_session()
│   ├── models/                # Modèles SQLModel (tables)
│   │   ├── user.py
│   │   ├── formation.py
│   │   ├── session.py
│   │   └── enrollment.py
│   ├── schemas/               # DTOs Pydantic (Create / Update / Read)
│   │   ├── user.py
│   │   ├── formation.py
│   │   ├── session.py
│   │   └── enrollement.py
│   ├── repositories/          # Accès données (CRUD par entité)
│   │   ├── user_repo.py
│   │   ├── formation_repo.py
│   │   ├── session_repo.py
│   │   └── enrollment_repo.py
│   ├── services/              # Règles métier (orchestration, validation)
│   │   ├── user_service.py
│   │   ├── formation_service.py
│   │   ├── session_service.py
│   │   └── enrollment_service.py
│   ├── api/v1/
│   │   ├── router.py          # Agrégation des routeurs
│   │   ├── users.py
│   │   ├── formations.py
│   │   ├── sessions.py
│   │   └── enrollment.py
│   └── utils/
│       └── enum.py            # Role, Level, SessionStatus
│
├── alembic/
│   ├── env.py
│   └── versions/
├── docker/
│   └── initdb/                # Scripts SQL au démarrage du conteneur
└── tests/
    ├── conftest.py            # Fixture client (TestClient), base de test
    ├── test_api_users.py
    ├── test_api_formations.py
    ├── test_api_sessions.py
    └── test_api_enrollments.py
```

Architecture en couches : **routes** → **services** → **repositories** → **modèles**. Les **schémas** Pydantic assurent la validation des entrées (Create/Update) et la sérialisation des sorties (Read).

---

## Modèles et relations

| Entité      | Table        | Rôle |
|------------|--------------|------|
| **User**   | `users`      | Admin, formateur ou apprenant. Champs : email (unique), first_name, last_name, role, registered_at, updated_at. Relations : sessions animées (`taught_sessions`), inscriptions (`enrollments`). |
| **Formation** | `formations` | Titre, description, duration_hours, level (0/1/2), created_at, updated_at. Relation : `sessions`. |
| **Session**   | `sessions`   | formation_id, teacher_id, start_date, end_date, capacity_max, status. Relations : formation, teacher (User), enrollments. |
| **Enrollment** | `enrollments` | session_id, student_id, enrolled_at. Contrainte unique `(session_id, student_id)` : un apprenant ne peut être inscrit qu’une fois par session. |

Les noms de tables sont au pluriel (`users`, `formations`, `sessions`, `enrollments`).

---

## Migrations (Alembic)

Les migrations utilisent `DATABASE_URL` (chargée depuis `.env` dans `alembic/env.py`).

```bash
# Créer une révision après modification des modèles
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière d’une révision
alembic downgrade -1
```

Le métadonnées Alembic viennent de `app.db.base` (`target_metadata = SQLModel.metadata`). Tous les modèles doivent être importés dans `app/db/base.py` pour être pris en compte par l’autogenerate.

---

## Tests automatisés

### Exécution

```bash
# Tous les tests (base de test utilisée automatiquement si TEST_DATABASE_URL est définie)
pytest

# Avec couverture
pytest --cov=app --cov-report=term-missing
```

Les tests fixent `USE_TEST_DB=1` avant l’import de l’app : l’application utilise alors `TEST_DATABASE_URL` pour se connecter à la base de test. Sans `TEST_DATABASE_URL`, les tests utilisent `DATABASE_URL`.

### Organisation des tests

| Fichier                  | Contenu |
|--------------------------|--------|
| `conftest.py`            | Fixture `client` (TestClient FastAPI), activation de la base de test. |
| `test_api_users.py`      | CRUD utilisateurs, validation (email, rôle, nom/prénom), conflits (email déjà utilisé). |
| `test_api_formations.py` | CRUD formations, validation (titre, durée, niveau), conflits (titre déjà utilisé). |
| `test_api_sessions.py`   | CRUD sessions, listes par formation/formateur/dates, erreurs (formation/formateur absents, dates, user non formateur). |
| `test_api_enrollments.py`| Création/suppression d’inscriptions, capacité, unicité (session, apprenant), listes par session/étudiant. |

Couverture recommandée : **≥ 70 %** (le projet vise une couverture élevée sur le module `app/`).

---

## Gestion des erreurs

### Erreurs de validation (422)

Les erreurs Pydantic sont reformatées en français avec un code unique :

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Champs invalides ou manquants : email, first_name.",
  "details": [
    { "field": "email", "message": "Champ requis" },
    { "field": "first_name", "message": "Champ requis" }
  ]
}
```

### Erreurs métier (4xx)

Réponses JSON avec `code` et `message` :

| Code HTTP | Exemples de `code` métier |
|-----------|----------------------------|
| 404       | `USER_NOT_FOUND`, `FORMATION_NOT_FOUND`, `SESSION_NOT_FOUND`, `ENROLLMENT_NOT_FOUND`, `TEACHER_NOT_FOUND` |
| 409       | `EMAIL_ALREADY_USED`, `FORMATION_TITLE_ALREADY_USED`, `ENROLLMENT_ALREADY_EXISTS` |
| 400       | `SESSION_START_DATE_AFTER_END_DATE`, `SESSION_START_DATE_ALREADY_EXISTS`, `SESSION_END_DATE_ALREADY_EXISTS`, `USER_NOT_TRAINER`, `ENROLLMENT_SESSION_FULL` |

Exemple :

```json
{
  "code": "EMAIL_ALREADY_USED",
  "message": "This email is already used."
}
```

---

## Licence et contact

Projet à usage pédagogique / démonstration. Pour toute question sur le code ou l’architecture, se référer au dépôt ou à l’équipe projet.
