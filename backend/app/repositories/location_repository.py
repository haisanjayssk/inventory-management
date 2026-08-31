from app.repositories.base_repository import BaseRepository

class LocationRepository(BaseRepository):
    def __init__(self):
        super().__init__("locations")

    def find_by_code(self, location_code: str, session=None):
        return self.find_one({"location_code": location_code}, session=session)

    def find_by_nfc(self, nfc_tag_uid: str, session=None):
        # Support full URI match or plain code match
        return self.find_one({
            "$or": [
                {"nfc_tag_uid": nfc_tag_uid},
                {"nfc_tag_uid": f"inventory://location/{nfc_tag_uid}"},
                {"location_code": nfc_tag_uid}
            ]
        }, session=session)

    def find_active_locations(self, session=None):
        return self.find_all({"status": "ACTIVE"}, session=session)
