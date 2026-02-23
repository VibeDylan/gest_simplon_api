from fastapi import APIRouter
from app.repositories.formation_repo import FormationRepository
from app.schemas.formation import FormationCreate, FormationRead, FormationUpdate
from sqlmodel import Session
from typing import List
from app.services.formation_service import FormationService
from app.db.session import get_session
from fastapi import Depends
router = APIRouter(prefix="/formations", tags=["formations"])

def get_formation_service(session: Session = Depends(get_session)) -> FormationService:
    """Injecte session → repository → service pour les routes users."""
    repo = FormationRepository(session)
    return FormationService(repo)