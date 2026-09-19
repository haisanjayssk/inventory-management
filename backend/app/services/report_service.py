from app.config.database import Database
from app.services.inventory_service import InventoryService
from app.services.location_service import LocationService
from app.services.transaction_service import TransactionService

class ReportService:
    def __init__(self):
        self.inv_service = InventoryService()
        self.loc_service = LocationService()
        self.txn_service = TransactionService()

    def get_stock_by_item_report(self, org_id: str = "ORG-001"):
        db = Database.get_db()
        if db is None:
            return []

        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"organization_id": org_id},
                        {"organization_id": {"$exists": False}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "$ifNull": ["$item_id", "$part_id"]
                    },
                    "total_quantity": {"$sum": {"$ifNull": ["$quantity", 1]}},
                    "available_quantity": {"$sum": {"$ifNull": ["$available_quantity", {"$ifNull": ["$quantity", 1]}]}},
                    "reserved_quantity": {"$sum": {"$ifNull": ["$reserved_quantity", 0]}},
                    "location_count": {"$addToSet": "$location_id"},
                    "lot_count": {"$addToSet": {"$ifNull": ["$lot_number", "$lot_id"]}}
                }
            }
        ]
        results = list(db.inventory.aggregate(pipeline))
        enriched = []
        for r in results:
            item_id = r["_id"]
            if not item_id:
                continue
            item = db.items.find_one({"_id": item_id}) or db.parts.find_one({"_id": item_id})
            code = item.get("code") or item.get("part_code", item_id) if item else item_id
            name = item.get("name") or item.get("part_name", "") if item else ""
            mpn = item.get("mpn", "") if item else ""
            unit = item.get("unit_of_measure", "PCS") if item else "PCS"
            enriched.append({
                "item_id": item_id,
                "part_id": item_id,
                "code": code,
                "part_code": code,
                "name": name,
                "part_name": name,
                "mpn": mpn,
                "unit": unit,
                "total_quantity": r["total_quantity"],
                "available_quantity": r["available_quantity"],
                "reserved_quantity": r["reserved_quantity"],
                "locations_count": len([l for l in r["location_count"] if l]),
                "lots_count": len([l for l in r["lot_count"] if l])
            })
        return sorted(enriched, key=lambda x: str(x.get("code", "")))

    def get_stock_by_part_report(self, org_id: str = "ORG-001"):
        return self.get_stock_by_item_report(org_id)

    def get_location_occupancy_report(self, org_id: str = "ORG-001"):
        return self.loc_service.get_all_locations(org_id)
