from app.repositories.base_repository import BaseRepository

class OrganizationRepository(BaseRepository):
    def __init__(self):
        super().__init__("organizations")

    def find_by_code(self, code: str, session=None):
        return self.find_one({"code": code.strip().upper()}, session=session)
