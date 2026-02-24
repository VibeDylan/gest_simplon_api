# GestSimplon API

API REST FastAPI pour la gestion de formations, sessions et inscriptions (apprenants / formateurs). Projet type “gestion Simplon”.

---

## Sommaire

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancer le projet](#lancer-le-projet)
- [Migrations (Alembic)](#migrations-alembic)
- [Structure du projet](#structure-du-projet)
- [Modèles et relations](#modèles-et-relations)
- [Tests](#tests)

---

## Prérequis

- **Python 3.11+**
- **PostgreSQL** (ou Docker pour lancer Postgres en conteneur)
- **pip** / **venv**

---

## Installation

```bash
# Cloner le dépôt (si besoin)
git clone <repo_url>
cd gestsimplon

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## Configuration

### Variables d'environnement

Copier `.env.example` vers `.env` et adapter les valeurs :

```bash
cp .env.example .env
```

| Variable         | Description                    | Exemple                                      |
|------------------|--------------------------------|----------------------------------------------|
| `POSTGRES_USER`  | Utilisateur Postgres           | `postgres`                                   |
| `POSTGRES_PASSWORD` | Mot de passe Postgres       | `postgres`                                   |
| `POSTGRES_DB`    | Nom de la base                 | `gestsimplon`                                |
| `DATABASE_URL`   | URL de connexion complète      | `postgresql://postgres:postgres@localhost:5444/gestsimplon` |
| `ENV`            | Environnement (optionnel)     | `dev` (défaut)                               |

Le port **5444** dans `DATABASE_URL` correspond au mapping Docker (`5444:5432`). Si Postgres tourne en local sur 5432, adapter l’URL.

### Base de données avec Docker

```bash
docker compose up -d
```

Postgres est exposé sur le port **5444** (hôte). Les données sont persistées dans le volume `postgres_data`.

---

## Lancer le projet
```bash
# Avec uvicorn (depuis la racine du projet)
uvicorn main:app --reload
```

- API : **http://127.0.0.1:8000**
- Docs Swagger : **http://127.0.0.1:8000/docs**

---

## Migrations (Alembic)

Les migrations utilisent **DATABASE_URL** depuis `.env` (voir `alembic/env.py`).

```bash
# Créer une nouvelle révision (après modification des modèles)
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière d’une révision
alembic downgrade -1
```

Le metadata Alembic est fourni par `app.db.base` (`target_metadata = SQLModel.metadata`). Tous les modèles doivent être importés dans `app/db/base.py` pour être pris en compte par l’autogenerate.

---

## Structure du projet

```
gestsimplon/
├── main.py                 # Point d’entrée FastAPI
├── requirements.txt        # Dépendances (FastAPI, SQLModel, Pydantic v2, Pytest, ...)
├── docker-compose.yml      # Postgres
├── alembic.ini
├── .env.example / .env
│
├── app/
│   ├── core/
│   │   └── config.py       # Settings (pydantic-settings, DATABASE_URL, ENV)
│   ├── db/
│   │   ├── base.py         # Metadata pour Alembic, imports des modèles
│   │   └── session.py      # Engine + get_session() (SQLModel Session)
│   ├── models/             # Modèles SQLModel (tables)
│   │   ├── user.py         # Role, User (admin / trainer / learner)
│   │   ├── formation.py    # Level, Formation
│   │   ├── session.py      # SessionStatus, Session
│   │   └── enrollment.py   # Enrollment (inscription Session ↔ Apprenant)
│   ├── schemas/            # DTOs Pydantic (validation entrée/sortie)
│   │   ├── user.py         # UserCreate, UserUpdate, UserRead
│   │   ├── formation.py    # FormationCreate, FormationUpdate, FormationRead
│   │   ├── session.py      # SessionCreate, SessionUpdate, SessionRead
│   │   └── enrollement.py  # EnrollmentCreate, EnrollmentUpdate, EnrollmentRead
│   ├── repositories/       # Accès données (CRUD par entité, SQLModel)
│   │   ├── user_repo.py       # UserRepository
│   │   ├── formation_repo.py  # FormationRepository (pagination, filtres)
│   │   ├── session_repo.py    # SessionRepository (pagination, filtres, recherches)
│   │   └── enrollment_repo.py # EnrollmentRepository
│   ├── services/           # Services métier (règles métiers + orchestrations)
│   │   ├── user_service.py       # Emails uniques, rôles
│   │   ├── formation_service.py  # Titre unique, durée > 0
│   │   ├── session_service.py    # Vérif formation / formateur, dates, capacité
│   │   └── enrollment_service.py # Unicité (session_id, student_id), capacité, session existante
│   ├── api/
│   │   └── v1/
│   │       ├── users.py        # Routes CRUD utilisateurs
│   │       ├── formations.py   # Routes CRUD formations
│   │       ├── sessions.py     # Routes CRUD + filtres sessions
│   │       ├── enrollment.py   # Routes inscriptions (créer, lister, désinscrire)
│   │       └── router.py       # Agrégation des routeurs v1
│   └── utils/
│       └── enum.py         # Enums partagées (Role, Level, SessionStatus)
│
├── alembic/
│   ├── env.py              # Utilise settings.database_url
│   └── versions/
└── docs/
    └── ARCHITECTURE.md     # Détails architecture et conventions
```

---

## Modèles et relations

- **User** (`users`) : rôles admin / formateur (trainer) / apprenant (learner). Liens : `taught_sessions`, `enrollments`.
- **Formation** (`formations`) : titre, niveau, durée. Lien : `sessions`.
- **Session** (`sessions`) : liée à une formation, un formateur (User), dates, capacité, statut. Lien : `enrollments`.
- **Enrollment** (`enrollments`) : table d’association Session ↔ Apprenant. Contrainte unique `(session_id, student_id)` : un apprenant ne peut être inscrit qu’une fois par session.

Tables Postgres : `users`, `formations`, `sessions`, `enrollments` (noms au pluriel pour éviter les mots réservés).

Détails des relations et conventions : voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Tests

```bash
pytest
pytest --cov=app   # avec couverture
```

Dépendances : `pytest`, `pytest-cov` (dans `requirements.txt`).

Les tests d’API principaux sont organisés par ressource dans `tests/` :

```text
tests/
├── conftest.py            # client FastAPI, fixtures DB
├── test_api_users.py      # CRUD utilisateurs + erreurs
├── test_api_formations.py # CRUD formations + pagination/filtres
├── test_api_sessions.py   # CRUD sessions + filtres par formation / formateur / dates
└── test_api_enrollments.py# Inscriptions (création, capacité, unicité, désinscription)
```

Les erreurs de validation Pydantic sont centralisées dans `main.py` et renvoyées sous la forme :

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

Les dates des sessions / inscriptions attendent le format **datetime ISO 8601** en JSON, par ex. :

```json
{
  "formation_id": 1,
  "teacher_id": 2,
  "start_date": "2025-10-12T09:00:00",
  "end_date": "2025-10-12T17:00:00",
  "capacity_max": 20,
  "status": "scheduled"
}
```

