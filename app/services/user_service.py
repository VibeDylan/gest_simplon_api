"""
Service métier pour les utilisateurs.

Orchestre le repository et applique les règles métier (unicité email, levée d'exceptions).
"""
from typing import List, Optional

from pydantic import EmailStr

from app.core.errors import EmailAlreadyUsed, UserNotFound
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create(self, data: UserCreate) -> User:
        email = data.email.lower().strip()
        if self.repo.get_by_email(email):
            raise EmailAlreadyUsed()
        return self.repo.create(data)

    def get_by_id(self, id: int) -> User:
        user = self.repo.get_by_id(id)
        if not user:
            raise UserNotFound()
        return user

    def get_by_email(self, email: EmailStr) -> User:
        email = email.lower().strip()
        user = self.repo.get_by_email(email)
        if not user:
            raise UserNotFound()
        return user

    def list(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Liste paginée d'utilisateurs (délègue au repo, pas d'exception si vide)."""
        return self.repo.list(offset=offset, limit=limit)

    def update(self, id: int, data: UserUpdate) -> User:
        user = self.repo.update(id, data)
        if not user:
            raise UserNotFound()
        return user

    def delete(self, id: int) -> bool:
        deleted = self.repo.delete(id)
        if not deleted:
            raise UserNotFound()
        return deleted