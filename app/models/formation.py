from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Formation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=2)
    description: Optional[str] = Field(default=None)
    duration_hours: int = Field(gt=0) 
    level: Level = Field(default=Level.BEGINNER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})