from app.repositories.base_repository import BaseRepository

class PartTypeRepository(BaseRepository):
    def __init__(self):
        super().__init__("part_types")

class PartTypeFieldRepository(BaseRepository):
    def __init__(self):
        super().__init__("part_type_fields")

    def find_by_part_type(self, part_type_id: str, session=None):
        return self.find_all({"part_type_id": part_type_id, "active": True}, session=session)

class VendorRepository(BaseRepository):
    def __init__(self):
        super().__init__("vendors")

class PartRepository(BaseRepository):
    def __init__(self):
        super().__init__("parts")

    def find_by_code(self, part_code: str, session=None):
        return self.find_one({"part_code": part_code}, session=session)

class LotRepository(BaseRepository):
    def __init__(self):
        super().__init__("lots")

    def find_by_part_and_batch(self, part_id: str, lot_batch_no: str, session=None):
        return self.find_one({"part_id": part_id, "lot_batch_no": lot_batch_no}, session=session)
