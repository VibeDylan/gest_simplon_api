class FormationService:
    def __init__(self, repo: FormationRepository):
        self.repo = repo

    def create(self, data: FormationCreate) -> Formation:
        return self.repo.create(data)

    def get_by_id(self, id: int) -> Formation:
        return self.repo.get_by_id(id)

    def list(self, offset: int = 0, limit: int = 100) -> List[Formation]:
        return self.repo.list(offset=offset, limit=limit)