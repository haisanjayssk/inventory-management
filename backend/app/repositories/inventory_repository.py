from app.repositories.base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    def __init__(self):
        super().__init__("inventory")

    def find_by_keys(self, org_id: str, item_id: str, location_id: str,
                     lot_number: str = None, serial_number: str = None, session=None):
        query = {
            "organization_id": org_id,
            "item_id": item_id,
            "location_id": location_id,
            "lot_number": lot_number,
            "serial_number": serial_number
        }
        return self.find_one(query, session=session)

    def find_by_serial(self, org_id: str, serial_number: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "serial_number": serial_number.strip()
        }, session=session)

    def find_by_item(self, org_id: str, item_id: str, session=None):
        return self.find_all({
            "organization_id": org_id,
            "$or": [{"item_id": item_id}, {"part_id": item_id}]
        }, session=session)

    def find_by_location(self, org_id: str, location_id: str, session=None):
        return self.find_all({
            "organization_id": org_id,
            "location_id": location_id
        }, session=session)

    def find_by_part(self, part_id: str, org_id: str = "ORG-001", session=None):
        return self.find_by_item(org_id, part_id, session=session)

    # Legacy alias
    def find_by_part_lot_location(self, part_id: str, lot_id: str, location_id: str, session=None):
        return self.find_one({
            "$or": [
                {"item_id": part_id, "lot_number": lot_id, "location_id": location_id},
                {"part_id": part_id, "lot_id": lot_id, "location_id": location_id}
            ]
        }, session=session)
