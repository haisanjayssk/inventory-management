from app.repositories.base_repository import BaseRepository

class IndentRepository(BaseRepository):
    def __init__(self):
        super().__init__("indents")

    def find_by_indent_number(self, indent_number: str, session=None):
        return self.find_one({"indent_number": indent_number}, session=session)

    def find_by_project(self, project_id: str, session=None):
        return self.find_all({"project_id": project_id}, session=session)

    def find_by_status(self, status: str, session=None):
        return self.find_all({"status": status}, session=session)

    def find_by_requester(self, requester_id: str, session=None):
        return self.find_all({"requester_id": requester_id}, session=session)

    def find_by_project_head(self, project_head_id: str, session=None):
        return self.find_all({"project_head_id": project_head_id}, session=session)
