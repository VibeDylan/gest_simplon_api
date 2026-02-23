from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.formation import Formation
    from app.models.user import User


class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    formation_id: int = Field(foreign_key="formations.id")
    teacher_id: int = Field(foreign_key="users.id")
    start_date: datetime
    end_date: datetime
    capacity_max: int = Field(ge=1, default=1)
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)

    formation: "Formation" = Relationship(back_populates="sessions")
    teacher: "User" = Relationship(back_populates="taught_sessions")
    enrollments: list["Enrollment"] = Relationship(back_populates="session")
