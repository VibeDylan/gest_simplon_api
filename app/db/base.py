"""
Registre des modèles pour Alembic.
Importe tous les modèles pour peupler SQLModel.metadata, puis expose target_metadata.
"""
from sqlmodel import SQLModel

from app.models.enrollment import Enrollment
from app.models.formation import Formation
from app.models.session import Session
from app.models.user import User

__all__ = ["SQLModel", "User", "Formation", "Session", "Enrollment", "target_metadata"]

target_metadata = SQLModel.metadata
