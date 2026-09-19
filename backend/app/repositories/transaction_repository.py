from app.repositories.base_repository import BaseRepository
from pymongo import DESCENDING

class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__("inventory_transactions")

    def get_history_for_serial(self, org_id: str, serial_number: str, session=None):
        s = serial_number.strip()
        return self.find_all(
            {
                "organization_id": org_id,
                "$or": [
                    {"serial_number": s},
                    {"serial_number": {"$regex": s}},
                    {"reference.serial_number": s},
                    {"cell_id": s}
                ]
            },
            sort_by=[("timestamp", DESCENDING)],
            session=session
        )

    def get_history_for_item(self, org_id: str, item_id: str, limit: int = 50, session=None):
        return self.find_all(
            {"organization_id": org_id, "$or": [{"item_id": item_id}, {"part_id": item_id}]},
            sort_by=[("timestamp", DESCENDING)],
            limit=limit,
            session=session
        )

    def get_history_for_location(self, org_id: str, location_id: str, limit: int = 50, session=None):
        return self.find_all(
            {
                "organization_id": org_id,
                "$or": [{"from_location_id": location_id}, {"to_location_id": location_id}]
            },
            sort_by=[("timestamp", DESCENDING)],
            limit=limit,
            session=session
        )

    def get_history_by_batch(self, org_id: str, t_id: str, session=None):
        return self.find_all(
            {"organization_id": org_id, "t_id": t_id},
            sort_by=[("timestamp", DESCENDING)],
            session=session
        )

    # Legacy aliases
    def get_history_for_cell(self, cell_id: str, session=None):
        return self.get_history_for_serial("ORG-001", cell_id, session=session)

    def get_history_for_part(self, part_id: str, limit: int = 50, session=None):
        return self.get_history_for_item("ORG-001", part_id, limit=limit, session=session)
