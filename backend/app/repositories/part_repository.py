from app.repositories.item_repository import ItemRepository
from app.repositories.item_type_repository import ItemTypeRepository
from app.repositories.vendor_repository import VendorRepository
from app.repositories.base_repository import BaseRepository

class PartTypeRepository(ItemTypeRepository):
    def __init__(self):
        super().__init__()

class PartTypeFieldRepository(BaseRepository):
    def __init__(self):
        super().__init__("part_type_fields")

    def find_by_part_type(self, part_type_id: str, session=None):
        return self.find_all({"part_type_id": part_type_id, "active": True}, session=session)

class PartRepository(ItemRepository):
    def __init__(self):
        super().__init__()

    def find_by_code(self, part_code: str, session=None):
        if isinstance(part_code, str):
            return self.find_one({
                "$or": [
                    {"code": part_code.strip().upper()},
                    {"part_code": part_code.strip().upper()}
                ]
            }, session=session)
        return None

class LotRepository(BaseRepository):
    def __init__(self):
        super().__init__("lots")

    def find_by_part_and_batch(self, part_id: str, lot_batch_no: str, session=None):
        return self.find_one({"part_id": part_id, "lot_batch_no": lot_batch_no}, session=session)

__all__ = [
    "PartTypeRepository",
    "PartTypeFieldRepository",
    "VendorRepository",
    "PartRepository",
    "LotRepository"
]
