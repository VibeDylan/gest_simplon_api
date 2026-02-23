from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import utcnow


class Role(str, Enum):
    ADMIN = "admin"
    TRAINER = "trainer" 
    LEARNER = "learner"   


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    registered_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"onupdate": utcnow},
    )
    role: Role = Field(default=Role.LEARNER)
