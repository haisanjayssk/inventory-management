from app.repositories.inventory_repository import InventoryRepository
from app.repositories.part_repository import PartRepository, LotRepository, PartTypeRepository, VendorRepository
from app.repositories.location_repository import LocationRepository

class InventoryService:
    def __init__(self):
        self.inv_repo = InventoryRepository()
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()
        self.part_type_repo = PartTypeRepository()
        self.vendor_repo = VendorRepository()
        self.location_repo = LocationRepository()

    def get_all_inventory(self, search: str = None, part_type_id: str = None, vendor_id: str = None,
                          location_id: str = None, status: str = None, skip: int = 0, limit: int = 100):
        query = {}
        if location_id:
            query["location_id"] = location_id
        if status:
            query["status"] = status

        items = self.inv_repo.find_all(query, sort_by=[("updated_at", -1)], skip=skip, limit=limit)
        total_count = self.inv_repo.count(query)

        enriched = []
        for inv in items:
            part = self.part_repo.find_by_id(inv.get("part_id"))
            lot = self.lot_repo.find_by_id(inv.get("lot_id"))
            loc = self.location_repo.find_by_id(inv.get("location_id"))

            if part_type_id and part and part.get("part_type_id") != part_type_id:
                continue
            if vendor_id and part and part.get("vendor_id") != vendor_id:
                continue

            if search:
                s_lower = search.lower()
                p_code = (part.get("part_code") if part else "").lower()
                p_name = (part.get("part_name") if part else "").lower()
                l_code = (loc.get("location_code") if loc else "").lower()
                lot_no = (lot.get("lot_batch_no") if lot else "").lower()
                if not (s_lower in p_code or s_lower in p_name or s_lower in l_code or s_lower in lot_no):
                    continue

            pt = self.part_type_repo.find_by_id(part.get("part_type_id")) if part else None
            v = self.vendor_repo.find_by_id(part.get("vendor_id")) if part else None

            enriched.append({
                "_id": inv["_id"],
                "part_id": inv.get("part_id"),
                "part_code": part.get("part_code") if part else None,
                "part_name": part.get("part_name") if part else None,
                "part_type_name": pt.get("part_type_name") if pt else None,
                "vendor_name": v.get("vendor_name") if v else None,
                "unit_of_measure": part.get("unit_of_measure", "PCS") if part else "PCS",
                "lot_id": inv.get("lot_id"),
                "lot_batch_no": lot.get("lot_batch_no") if lot else None,
                "location_id": inv.get("location_id"),
                "location_code": loc.get("location_code") if loc else None,
                "nfc_tag_uid": loc.get("nfc_tag_uid") if loc else None,
                "quantity": inv.get("quantity", 0),
                "available_quantity": inv.get("available_quantity", 0),
                "reserved_quantity": inv.get("reserved_quantity", 0),
                "reserved_for": inv.get("reserved_for"),
                "reserved_by": inv.get("reserved_by"),
                "status": inv.get("status", "AVAILABLE"),
                "updated_at": inv.get("updated_at")
            })

        return {
            "total": total_count,
            "items": enriched
        }
