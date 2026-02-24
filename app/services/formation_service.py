"""
Service métier pour les formations.

Orchestre le repository et applique les règles métier (unicité du titre, levée d'exceptions).
"""
from typing import List, Optional

from app.core.errors import FormationNotFound, FormationTitleAlreadyUsed
from app.models.formation import Formation
from app.repositories.formation_repo import FormationRepository
from app.schemas.formation import FormationCreate, FormationUpdate
from app.utils.enum import Level


class FormationService:
    """Orchestre le repository formation et les règles métier (unicité du titre)."""

    def __init__(self, repo: FormationRepository):
        """Initialise le service avec le repository injecté."""
        self.repo = repo

    def find_by_title(self, title: str) -> Optional[Formation]:
        """
        Cherche une formation par titre (finder interne, pas d'exception).

        Utile dans create/update pour vérifier l'unicité sans lever 404.
        """
        return self.repo.get_by_title(title)

    def create(self, data: FormationCreate) -> Formation:
        """Crée une formation. Lève FormationTitleAlreadyUsed si le titre existe déjà."""
        title = (data.title or "").strip()
        if self.find_by_title(title):
            raise FormationTitleAlreadyUsed()
        return self.repo.create(data)

    def get_by_id(self, id: int) -> Formation:
        """Retourne la formation d'id donné ou lève FormationNotFound."""
        formation = self.repo.get_by_id(id)
        if not formation:
            raise FormationNotFound()
        return formation

    def list(
        self,
        offset: int = 0,
        limit: int = 100,
        level: Optional[Level] = None,
        title_contains: Optional[str] = None,
    ) -> List[Formation]:
        """Liste paginée de formations avec filtres optionnels (pas d'exception si vide)."""
        return self.repo.list(
            offset=offset,
            limit=limit,
            level=level,
            title_contains=title_contains,
        )

    def update(self, id: int, data: FormationUpdate) -> Formation:
        """Met à jour une formation. Lève FormationNotFound si absente, FormationTitleAlreadyUsed si le nouveau titre est déjà pris."""
        formation = self.get_by_id(id)
        if data.title is not None:
            new_title = data.title.strip()
            if new_title and new_title.lower() != (formation.title or "").lower():
                existing = self.find_by_title(new_title)
                if existing is not None and existing.id != id:
                    raise FormationTitleAlreadyUsed()
        updated = self.repo.update(id, data)
        if updated is None:
            raise FormationNotFound()
        return updated

    def delete(self, id: int) -> bool:
        """Supprime la formation par id. Lève FormationNotFound si absente."""
        deleted = self.repo.delete(id)
        if not deleted:
            raise FormationNotFound()
        return deleted
