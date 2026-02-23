from pydantic import EmailStr
from app.utils.enum import Role
from pydantic import BaseModel, ConfigDict
from typing import Any
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: Role = Role.LEARNER

    model_config = ConfigDict(str_strip_whitespace=True)

    def model_post_init(self, __context: Any):
        self.email = self.email.lower()


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[Role] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    def model_post_init(self, __context: Any):
        if self.email:
            self.email = self.email.lower()

class UserRead(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: Role
    registered_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)