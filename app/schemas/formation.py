from pydantic import BaseModel
from typing import Optional
from app.utils.enum import Level
from pydantic import ConfigDict
from typing import Any

class FormationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: int
    level: Level

    model_config = ConfigDict(str_strip_whitespace=True)
    def model_post_init(self, __context: Any):
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else None
        self.duration_hours = int(self.duration_hours)
        self.level = Level(self.level)
