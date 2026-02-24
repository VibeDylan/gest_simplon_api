"""
Énumérations partagées entre modèles et schémas.

Role est utilisé par le modèle User et les schémas UserCreate / UserUpdate / UserRead.
"""
from enum import Enum


class Role(str, Enum):
    """Rôle utilisateur : administrateur, formateur ou apprenant."""
    ADMIN = "admin"
    TRAINER = "trainer"
    LEARNER = "learner"


class Level(str, Enum):
    """Niveau de la formation : débutant, intermédiaire, avancé."""

    BEGINNER = 0
    INTERMEDIATE = 1
    ADVANCED = 2


class SessionStatus(str, Enum):
    """Statut d'une session : planifiée, en cours, terminée."""

    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"

