from app.repositories.formation_repo import FormationRepository
from app.schemas.formation import FormationCreate
from app.models.formation import Formation
class FormationService:
    def __init__(self, repo: FormationRepository):
        self.repo = repo

    def create(self, data: FormationCreate) -> Formation:
        return self.repo.create(data)