"""
Repository CRUD pour l'entité User.

Encapsule l'accès en base (création, lecture, mise à jour, suppression)
et la pagination de la liste (MAX_PAGE_SIZE).
"""
from typing import List, Optional

from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

MAX_PAGE_SIZE = 100


class UserRepository:
    """
    Accès données pour les utilisateurs.

    Utilise une session SQLModel injectée. Toutes les méthodes
    qui modifient les données font commit (create, update, delete).
    """

    def __init__(self, session: Session):
        """Initialise le repository avec la session SQLModel injectée."""
        self.session = session

    def create(self, data: UserCreate, *, hashed_password: str) -> User:
        """Crée un utilisateur en base et retourne l'instance avec id rempli."""
        payload = data.model_dump(exclude={"password"})
        payload["hashed_password"] = hashed_password
        user = User(**payload)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, id: int) -> Optional[User]:
        """Retourne l'utilisateur d'id donné ou None."""
        return self.session.get(User, id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Retourne l'utilisateur avec cet email (normalisé minuscules) ou None."""
        email = email.lower().strip()
        return self.session.exec(select(User).where(User.email == email)).first()

    def list(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Liste paginée d'utilisateurs. limit plafonné à MAX_PAGE_SIZE."""
        limit = min(limit, MAX_PAGE_SIZE)
        return list(
            self.session.exec(select(User).offset(offset).limit(limit)).all()
        )

    def update(
        self, id: int, data: UserUpdate, *, hashed_password: Optional[str] = None
    ) -> Optional[User]:
        """Met à jour l'utilisateur par id (champs fournis uniquement). Retourne None si absent."""
        user = self.get_by_id(id)
        if user is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        payload.pop("password", None)
        if hashed_password is not None:
            payload["hashed_password"] = hashed_password
        for key, value in payload.items():
            setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, id: int) -> bool:
        """Supprime l'utilisateur par id. Retourne True si supprimé, False si non trouvé."""
        user = self.get_by_id(id)
        if user is None:
            return False
        self.session.delete(user)
        self.session.commit()
        return True
