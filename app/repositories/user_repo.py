from typing import List, Optional

from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

MAX_PAGE_SIZE = 100


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, id: int) -> Optional[User]:
        return self.session.get(User, id)

    def get_by_email(self, email: str) -> Optional[User]:
        email = email.lower().strip()
        return self.session.exec(select(User).where(User.email == email)).first()

    def list(self, offset: int = 0, limit: int = 100) -> List[User]:
        limit = min(limit, MAX_PAGE_SIZE)
        return list(
            self.session.exec(select(User).offset(offset).limit(limit)).all()
        )

    def update(self, id: int, data: UserUpdate) -> Optional[User]:
        user = self.get_by_id(id)
        if user is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, id: int) -> bool:
        user = self.get_by_id(id)
        if user is None:
            return False
        self.session.delete(user)
        self.session.commit()
        return True
