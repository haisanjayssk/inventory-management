from app.repositories.base_repository import BaseRepository
from pymongo import DESCENDING

class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__("transactions")

    def get_history_for_cell(self, cell_id: str, session=None):
        return self.find_all(
            {"cell_id": cell_id},
            sort_by=[("timestamp", DESCENDING)],
            session=session
        )

    def get_history_for_part(self, part_id: str, limit: int = 50, session=None):
        return self.find_all(
            {"part_id": part_id},
            sort_by=[("timestamp", DESCENDING)],
            limit=limit,
            session=session
        )

    def get_history_for_location(self, location_id: str, limit: int = 50, session=None):
        return self.find_all(
            {"$or": [{"from_location_id": location_id}, {"to_location_id": location_id}]},
            sort_by=[("timestamp", DESCENDING)],
            limit=limit,
            session=session
        )
