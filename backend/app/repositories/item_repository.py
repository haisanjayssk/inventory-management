from app.repositories.base_repository import BaseRepository

class ItemRepository(BaseRepository):
    def __init__(self):
        super().__init__("items")

    def find_by_code(self, org_id: str, code: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "$or": [
                {"code": code.strip().upper()},
                {"part_code": code.strip().upper()}
            ]
        }, session=session)

    def find_all_by_org(self, org_id: str, item_type_id: str = None, active_only: bool = False, session=None):
        query = {"organization_id": org_id}
        if item_type_id:
            query["$or"] = [{"item_type_id": item_type_id}, {"part_type_id": item_type_id}]
        if active_only:
            query["active"] = True
        return self.find_all(query, sort_by=[("code", 1)], session=session)
