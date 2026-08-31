from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("users")

    def find_by_email(self, email: str, session=None):
        return self.find_one({"email": email.lower().strip()}, session=session)

    def find_by_username(self, username: str, session=None):
        return self.find_one({"username": username.lower().strip()}, session=session)

    def find_by_username_or_email(self, identifier: str, session=None):
        cleaned = identifier.lower().strip()
        return self.find_one({"$or": [{"email": cleaned}, {"username": cleaned}]}, session=session)
