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
