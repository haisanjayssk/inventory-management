from app.repositories.base_repository import BaseRepository

class VendorRepository(BaseRepository):
    def __init__(self):
        super().__init__("vendors")

    def find_by_code(self, org_id: str, code: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "code": code.strip().upper()
        }, session=session)

    def find_by_name(self, org_id: str, name: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "$or": [
                {"name": name.strip()},
                {"vendor_name": name.strip()}
            ]
        }, session=session)

    def find_all_by_org(self, org_id: str, session=None):
        return self.find_all({"organization_id": org_id}, sort_by=[("name", 1)], session=session)
