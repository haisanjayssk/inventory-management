from app.repositories.base_repository import BaseRepository

class IndentReturnRepository(BaseRepository):
    def __init__(self):
        super().__init__("indent_returns")

    def find_by_return_number(self, return_number: str, session=None):
        return self.find_one({"return_number": return_number}, session=session)

    def find_by_indent(self, indent_id: str, session=None):
        return self.find_all({"indent_id": indent_id}, session=session)

    def find_by_status(self, status: str, session=None):
        return self.find_all({"status": status}, session=session)

    def find_by_requester(self, requester_id: str, session=None):
        return self.find_all({"requester_id": requester_id}, session=session)
