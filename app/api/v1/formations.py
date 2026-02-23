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

@router.post("", response_model=FormationRead, status_code=201)
def create_formation(
    data: FormationCreate,
    service: FormationService = Depends(get_formation_service),
):
    """
    Crée une formation.
    """
    formation = service.create(data)
    return FormationRead.model_validate(formation)

@router.get("", response_model=List[FormationRead], status_code=200)
def list_formations(
    service: FormationService = Depends(get_formation_service),
    offset: int = 0,
    limit: int = 100,
):
    """
    Liste les formations.
    """
    formations = service.list(offset=offset, limit=limit)
    return [FormationRead.model_validate(formation) for formation in formations]

@router.get("/{id}", response_model=FormationRead, status_code=200)
def get_formation(
    id: int,
    service: FormationService = Depends(get_formation_service),
):
    """
    Récupère une formation par ID.
    """
    formation = service.get_by_id(id)
    return FormationRead.model_validate(formation)

@router.patch("/{id}", response_model=FormationRead, status_code=200)
def update_formation(
    id: int,
    data: FormationUpdate,
    service: FormationService = Depends(get_formation_service),
):
    """
    Met à jour une formation par ID.
    """
    formation = service.update(id, data)
    return FormationRead.model_validate(formation)

@router.delete("/{id}", status_code=204)
def delete_formation(
    id: int,
    service: FormationService = Depends(get_formation_service),
):
    """
    Supprime une formation par ID.
    """
    service.delete(id)
    return None
    