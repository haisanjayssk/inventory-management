from app.repositories.base_repository import BaseRepository

class CellRepository(BaseRepository):
    def __init__(self):
        super().__init__("cells")

    def find_by_serial(self, cell_serial_no: str, session=None):
        return self.find_one({"cell_serial_no": cell_serial_no}, session=session)

    def find_by_lot(self, lot_id: str, session=None):
        return self.find_all({"lot_id": lot_id}, session=session)

class CellInventoryRepository(BaseRepository):
    def __init__(self):
        super().__init__("cell_inventory")

    def find_by_cell_id(self, cell_id: str, session=None):
        return self.find_one({"cell_id": cell_id}, session=session)

    def find_by_location_id(self, location_id: str, session=None):
        return self.find_all({"location_id": location_id}, session=session)
