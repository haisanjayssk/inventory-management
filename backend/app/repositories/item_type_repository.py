from app.repositories.base_repository import BaseRepository

class ItemTypeRepository(BaseRepository):
    def __init__(self):
        super().__init__("item_types")

    def find_by_code(self, org_id: str, code: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "code": code.strip().upper()
        }, session=session)

    def find_by_name(self, org_id: str, name: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "name": name.strip()
        }, session=session)

    def find_all_by_org(self, org_id: str, active_only: bool = False, session=None):
        query = {"organization_id": org_id}
        if active_only:
            query["active"] = True
        return self.find_all(query, sort_by=[("name", 1)], session=session)
