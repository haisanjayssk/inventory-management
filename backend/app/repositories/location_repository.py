from app.repositories.base_repository import BaseRepository

class LocationRepository(BaseRepository):
    def __init__(self):
        super().__init__("locations")

    def find_by_code(self, org_id: str, location_code: str, session=None):
        loc_code = location_code.strip()
        return self.find_one({
            "organization_id": org_id,
            "location_code": loc_code
        }, session=session) or self.find_one({"location_code": loc_code}, session=session)

    def find_by_nfc(self, org_id: str, nfc_uid: str, session=None):
        tag = nfc_uid.strip()
        query = {
            "$or": [
                {"nfc_uid": tag},
                {"nfc_tag_uid": tag},
                {"nfc_uid": f"inventory://location/{tag}"},
                {"nfc_tag_uid": f"inventory://location/{tag}"},
                {"location_code": tag}
            ]
        }
        return self.find_one({"organization_id": org_id, **query}, session=session) or self.find_one(query, session=session)

    def find_by_qr(self, org_id: str, qr_code: str, session=None):
        qr = qr_code.strip()
        query = {
            "$or": [
                {"qr_code": qr},
                {"location_code": qr}
            ]
        }
        return self.find_one({"organization_id": org_id, **query}, session=session) or self.find_one(query, session=session)

    def find_all_by_org(self, org_id: str, status: str = None, loc_type: str = None, session=None):
        query = {"organization_id": org_id}
        if status:
            query["status"] = status
        if loc_type:
            query["type"] = loc_type.upper()
        return self.find_all(query, sort_by=[("location_code", 1)], session=session)

    def find_children(self, org_id: str, parent_id: str, session=None):
        return self.find_all({
            "organization_id": org_id,
            "parent_id": parent_id
        }, sort_by=[("location_code", 1)], session=session)

    def find_active_locations(self, session=None):
        return self.find_all({"status": "ACTIVE"}, session=session)
