from datetime import datetime
from typing import Optional, Optional
from sqlmodel import SQLModel, Field
    
class Signature(SQLModel, table=True):
    """
    Signature d'émargement par un utilisateur.

    Attributes:
        id: Clé primaire.
        session_id: Session concernée.
        user_id: Utilisateur qui signe.
    """

    __tablename__ = "signatures"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.id")
    user_id: int = Field(foreign_key="users.id")
    date: Optional[datetime] = None
    
    