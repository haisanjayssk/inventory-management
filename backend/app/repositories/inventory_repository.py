from app.repositories.base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    def __init__(self):
        super().__init__("inventory")

    def find_by_part_lot_location(self, part_id: str, lot_id: str, location_id: str, session=None):
        return self.find_one({
            "part_id": part_id,
            "lot_id": lot_id,
            "location_id": location_id
        }, session=session)

    def find_by_part(self, part_id: str, session=None):
        return self.find_all({"part_id": part_id}, session=session)

    def find_by_location(self, location_id: str, session=None):
        return self.find_all({"location_id": location_id}, session=session)
