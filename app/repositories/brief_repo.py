"""
Repository CRUD pour l'entité Brief.

Encapsule l'accès en base (création, lecture, mise à jour, suppression)
et les listes par session_id / student_id.
"""
from typing import List, Optional

from sqlmodel import Session, select

class BriefRepository:
    """
    Accès données pour les briefs.

    Utilise une session SQLModel injectée. Toutes les méthodes
    qui modifient les données font commit (create, update, delete).
    """
    def __init__(self, session: Session):
        self.session = session