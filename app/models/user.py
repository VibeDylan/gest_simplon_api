from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.session import Session


class Role(str, Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    LEARNER = "learner"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    role: Role = Field(default=Role.LEARNER)

    taught_sessions: list["Session"] = Relationship(back_populates="teacher")
    enrollments: list["Enrollment"] = Relationship(back_populates="student")
