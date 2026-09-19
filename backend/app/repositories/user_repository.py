from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("users")

    def find_by_email(self, email: str, org_id: str = None, session=None):
        query = {"email": email.lower().strip()}
        if org_id:
            query["organization_id"] = org_id
        return self.find_one(query, session=session)

    def find_by_username(self, username: str, org_id: str = None, session=None):
        query = {"username": username.lower().strip()}
        if org_id:
            query["organization_id"] = org_id
        return self.find_one(query, session=session)

    def find_by_username_or_email(self, identifier: str, org_id: str = None, session=None):
        cleaned = identifier.lower().strip()
        query = {"$or": [{"email": cleaned}, {"username": cleaned}]}
        if org_id:
            query["organization_id"] = org_id
        return self.find_one(query, session=session) or self.find_one({"$or": [{"email": cleaned}, {"username": cleaned}]}, session=session)

    def find_all_by_org(self, org_id: str, role: str = None, active_only: bool = False, session=None):
        query = {"organization_id": org_id}
        if role:
            query["role"] = role
        if active_only:
            query["status"] = "ACTIVE"
        return self.find_all(query, sort_by=[("created_at", -1)], session=session)
