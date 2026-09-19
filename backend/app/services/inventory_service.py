from app.repositories.inventory_repository import InventoryRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.item_type_repository import ItemTypeRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.vendor_repository import VendorRepository
from app.repositories.transaction_repository import TransactionRepository

class InventoryService:
    def __init__(self):
        self.inv_repo = InventoryRepository()
        self.item_repo = ItemRepository()
        self.item_type_repo = ItemTypeRepository()
        self.location_repo = LocationRepository()
        self.vendor_repo = VendorRepository()
        self.txn_repo = TransactionRepository()

    def get_all_inventory(self, org_id: str = "ORG-001", search: str = None, item_type_id: str = None,
                          location_id: str = None, status: str = None, is_serialized: bool = None,
                          skip: int = 0, limit: int = 100):
        query = {"organization_id": org_id}
        if location_id:
            query["location_id"] = location_id
        if status:
            query["status"] = status
        if is_serialized is True:
            query["serial_number"] = {"$ne": None}
        elif is_serialized is False:
            query["serial_number"] = None

        raw_items = self.inv_repo.find_all(query, sort_by=[("updated_at", -1)], skip=skip, limit=limit)
        total_count = self.inv_repo.count(query)

        # Caches
        items_cache = {i["_id"]: i for i in self.item_repo.find_all({"organization_id": org_id})}
        types_cache = {t["_id"]: t for t in self.item_type_repo.find_all_by_org(org_id)}
        locs_cache = {l["_id"]: l for l in self.location_repo.find_all({"organization_id": org_id})}
        vendors_cache = {v["_id"]: v for v in self.vendor_repo.find_all_by_org(org_id)}

        enriched = []
        for inv in raw_items:
            item = items_cache.get(inv.get("item_id"))
            loc = locs_cache.get(inv.get("location_id"))
            vendor = vendors_cache.get(inv.get("vendor_id")) if inv.get("vendor_id") else None
            it = types_cache.get(item.get("item_type_id")) if item else None

            if item_type_id and item and item.get("item_type_id") != item_type_id:
                continue

            if search:
                s_lower = search.lower()
                i_code = (item.get("code") if item else "").lower()
                i_name = (item.get("name") if item else "").lower()
                l_code = (loc.get("location_code") if loc else "").lower()
                lot_no = (inv.get("lot_number") or "").lower()
                s_num = (inv.get("serial_number") or "").lower()
                if not (s_lower in i_code or s_lower in i_name or s_lower in l_code or s_lower in lot_no or s_lower in s_num):
                    continue

            enriched.append({
                "_id": inv["_id"],
                "organization_id": inv.get("organization_id"),
                "item_id": inv.get("item_id"),
                "item_code": item.get("code") if item else None,
                "item_name": item.get("name") if item else None,
                "item_type_name": it.get("name") if it else None,
                "item_type_code": it.get("code") if it else None,
                "tracking_mode": it.get("tracking_mode", "QUANTITY") if it else "QUANTITY",
                "location_id": inv.get("location_id"),
                "location_code": loc.get("location_code") if loc else None,
                "nfc_uid": loc.get("nfc_uid") if loc else None,
                "qr_code": loc.get("qr_code") if loc else None,
                "lot_number": inv.get("lot_number"),
                "serial_number": inv.get("serial_number"),
                "quantity": inv.get("quantity", 0),
                "vendor_id": inv.get("vendor_id"),
                "vendor_name": vendor.get("name") if vendor else None,
                "site_id": inv.get("site_id"),
                "status": inv.get("status", "AVAILABLE"),
                "created_at": inv.get("created_at"),
                "updated_at": inv.get("updated_at"),

                # Legacy frontend compatibility aliases
                "part_id": inv.get("item_id"),
                "part_code": item.get("code") if item else None,
                "part_name": item.get("name") if item else None,
                "part_type_name": it.get("name") if it else None,
                "lot_batch_no": inv.get("lot_number"),
                "nfc_tag_uid": loc.get("nfc_uid") if loc else None,
                "available_quantity": inv.get("quantity", 0),
                "reserved_quantity": 0
            })

        return {
            "total": total_count,
            "items": enriched
        }

    def get_inventory_by_serial(self, serial_number: str, org_id: str = "ORG-001"):
        inv = self.inv_repo.find_by_serial(org_id, serial_number)
        if not inv:
            raise ValueError(f"No active inventory record for serial '{serial_number}'")
        item = self.item_repo.find_one({"_id": inv["item_id"], "organization_id": org_id})
        loc = self.location_repo.find_one({"_id": inv["location_id"], "organization_id": org_id})
        txns = self.txn_repo.get_history_for_serial(org_id, serial_number)

        cell_data = {
            "cell_id": inv["serial_number"],
            "cell_serial_no": inv["serial_number"],
            "serial_number": inv["serial_number"],
            "part_id": inv["item_id"],
            "item_id": inv["item_id"],
            "item_code": item.get("code") if item else None,
            "part_code": item.get("code") if item else None,
            "part_name": item.get("name") if item else None,
            "lot_number": inv.get("lot_number"),
            "lot_batch_no": inv.get("lot_number"),
            "status": inv.get("status", "AVAILABLE"),
            "location_code": loc.get("location_code") if loc else None,
            "location": loc or {}
        }

        return {
            **inv,
            "item_code": item.get("code") if item else None,
            "item_name": item.get("name") if item else None,
            "location_code": loc.get("location_code") if loc else None,
            "cell": cell_data,
            "history": txns
        }

    def get_inventory_by_part(self, part_id: str, org_id: str = "ORG-001"):
        item = self.item_repo.find_one({"_id": part_id, "organization_id": org_id})
        if not item:
            item = self.item_repo.find_by_code(org_id, part_id)
        if not item:
            item = self.item_repo.find_one({
                "organization_id": org_id,
                "$or": [{"_id": part_id}, {"code": part_id}, {"part_number": part_id}]
            })

        item_id = item["_id"] if item else part_id
        item_code = item.get("code") if item else part_id
        item_name = item.get("name") if item else ""

        raw_inv = self.inv_repo.find_all({
            "organization_id": org_id,
            "$or": [
                {"item_id": item_id},
                {"part_id": item_id},
                {"item_id": item_code},
                {"part_id": item_code}
            ],
            "quantity": {"$gt": 0}
        })

        locs_cache = {l["_id"]: l for l in self.location_repo.find_all({"organization_id": org_id})}
        vendors_cache = {v["_id"]: v for v in self.vendor_repo.find_all_by_org(org_id)}

        results = []
        for inv in raw_inv:
            loc = locs_cache.get(inv.get("location_id"))
            loc_code = loc.get("location_code") or loc.get("code") if loc else (inv.get("location_code") or inv.get("location_id") or "STORE-A1")
            vendor = vendors_cache.get(inv.get("vendor_id")) if inv.get("vendor_id") else None
            lot_num = inv.get("lot_number") or inv.get("lot_batch_no") or inv.get("lot_id") or "STANDARD"

            results.append({
                "_id": inv["_id"],
                "inventory_id": inv["_id"],
                "item_id": item_id,
                "part_id": item_id,
                "item_code": item_code,
                "part_code": item_code,
                "item_name": item_name,
                "part_name": item_name,
                "location_id": inv.get("location_id"),
                "location_code": loc_code,
                "warehouse_name": loc.get("warehouse_name") or loc.get("zone") if loc else None,
                "lot_number": lot_num,
                "lot_batch_no": lot_num,
                "lot_id": lot_num,
                "quantity": inv.get("quantity", 0),
                "available_quantity": inv.get("available_quantity", inv.get("quantity", 0)),
                "serial_number": inv.get("serial_number"),
                "vendor_name": vendor.get("name") if vendor else None,
                "status": inv.get("status", "AVAILABLE"),
                "updated_at": inv.get("updated_at")
            })

        return results
