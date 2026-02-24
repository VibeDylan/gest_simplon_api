"""
Service métier pour les utilisateurs.

Orchestre le repository et applique les règles métier (unicité email, levée d'exceptions).
"""
from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.core.errors import EmailAlreadyUsed, UserNotFound
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Orchestre le repository utilisateur et les règles métier (unicité email)."""

    def __init__(self, repo: UserRepository):
        """Initialise le service avec le repository injecté."""
        self.repo = repo

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Cherche un utilisateur par email (finder interne, pas d'exception).

        Utile dans create/update pour vérifier l'unicité sans lever 404.
        """
        email = email.lower().strip()
        return self.repo.get_by_email(email)

    def create(self, data: UserCreate) -> User:
        """Crée un utilisateur. Lève EmailAlreadyUsed si l'email est déjà pris."""
        email = data.email.lower().strip()
        if self.find_by_email(email):
            raise EmailAlreadyUsed()
        return self.repo.create(data)

    def get_by_id(self, id: int) -> User:
        """Retourne l'utilisateur d'id donné ou lève UserNotFound."""
        user = self.repo.get_by_id(id)
        if not user:
            raise UserNotFound()
        return user

    def get_by_email(self, email: EmailStr) -> User:
        """Retourne l'utilisateur avec cet email ou lève UserNotFound."""
        email = email.lower().strip()
        user = self.find_by_email(email)
        if not user:
            raise UserNotFound()
        return user

    def list(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Liste paginée d'utilisateurs (délègue au repo, pas d'exception si vide)."""
        return self.repo.list(offset=offset, limit=limit)

    def update(self, id: int, data: UserUpdate) -> User:
        """Met à jour l'utilisateur par id. Lève UserNotFound si absent, EmailAlreadyUsed si nouvel email déjà pris."""
        user = self.repo.get_by_id(id)
        if not user:
            raise UserNotFound()
        if data.email is not None:
            new_email = data.email.lower().strip()
            if new_email != (user.email or "").lower():
                existing = self.find_by_email(new_email)
                if existing is not None and existing.id != id:
                    raise EmailAlreadyUsed()
        try:
            updated = self.repo.update(id, data)
        except IntegrityError:
            raise EmailAlreadyUsed("This email is already used.")
        if updated is None:
            raise UserNotFound()
        return updated

    def delete(self, id: int) -> bool:
        """Supprime l'utilisateur par id. Lève UserNotFound si absent."""
        deleted = self.repo.delete(id)
        if not deleted:
            raise UserNotFound()
        return deleted