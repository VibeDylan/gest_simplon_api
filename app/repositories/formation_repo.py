"""
Repository CRUD pour l'entité Formation.

Encapsule l'accès en base (création, lecture, mise à jour, suppression),
la pagination et les filtres (niveau, recherche par titre).
"""
from typing import List, Optional

from sqlmodel import Session, select

from app.models.formation import Formation
from app.schemas.formation import FormationCreate, FormationUpdate
from app.utils.enum import Level

MAX_PAGE_SIZE = 100


class FormationRepository:
    """
    Accès données pour les formations.

    Utilise une session SQLModel injectée. Toutes les méthodes
    qui modifient les données font commit (create, update, delete).
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: FormationCreate) -> Formation:
        """Crée une formation en base et retourne l'instance avec id rempli."""
        formation = Formation(**data.model_dump())
        self.session.add(formation)
        self.session.commit()
        self.session.refresh(formation)
        return formation

    def get_by_id(self, id: int) -> Optional[Formation]:
        """Retourne la formation d'id donné ou None."""
        return self.session.get(Formation, id)

    def exists(self, id: int) -> bool:
        """Retourne True si une formation avec cet id existe, False sinon."""
        return self.get_by_id(id) is not None

    def list(
        self,
        offset: int = 0,
        limit: int = 100,
        level: Optional[Level] = None,
        title_contains: Optional[str] = None,
    ) -> List[Formation]:
        """
        Liste paginée de formations, avec filtres optionnels.

        limit est plafonné à MAX_PAGE_SIZE.
        level: filtre par niveau (beginner, intermediate, advanced).
        title_contains: filtre par titre (contient la chaîne, insensible à la casse).
        """
        limit = min(limit, MAX_PAGE_SIZE)
        stmt = select(Formation).offset(offset).limit(limit)
        if level is not None:
            stmt = stmt.where(Formation.level == level)
        if title_contains is not None and title_contains.strip():
            stmt = stmt.where(
                Formation.title.ilike(f"%{title_contains.strip()}%")
            )
        return list(self.session.exec(stmt).all())

    def update(self, id: int, data: FormationUpdate) -> Optional[Formation]:
        """Met à jour la formation par id (champs fournis uniquement). Retourne None si absente."""
        formation = self.get_by_id(id)
        if formation is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(formation, key, value)
        self.session.commit()
        self.session.refresh(formation)
        return formation

    def delete(self, id: int) -> bool:
        """Supprime la formation par id. Retourne True si supprimée, False si non trouvée."""
        formation = self.get_by_id(id)
        if formation is None:
            return False
        self.session.delete(formation)
        self.session.commit()
        return True
