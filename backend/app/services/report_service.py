from app.config.database import Database
from app.services.inventory_service import InventoryService
from app.services.location_service import LocationService
from app.services.transaction_service import TransactionService

class ReportService:
    def __init__(self):
        self.inv_service = InventoryService()
        self.loc_service = LocationService()
        self.txn_service = TransactionService()

    def get_stock_by_part_report(self):
        db = Database.get_db()
        pipeline = [
            {
                "$group": {
                    "_id": "$part_id",
                    "total_quantity": {"$sum": "$quantity"},
                    "available_quantity": {"$sum": "$available_quantity"},
                    "reserved_quantity": {"$sum": "$reserved_quantity"},
                    "location_count": {"$addToSet": "$location_id"},
                    "lot_count": {"$addToSet": "$lot_id"}
                }
            }
        ]
        results = list(db.inventory.aggregate(pipeline))
        enriched = []
        for r in results:
            part = db.parts.find_one({"_id": r["_id"]})
            if part:
                enriched.append({
                    "part_id": r["_id"],
                    "part_code": part.get("part_code"),
                    "part_name": part.get("part_name"),
                    "mpn": part.get("mpn"),
                    "unit": part.get("unit_of_measure", "PCS"),
                    "total_quantity": r["total_quantity"],
                    "available_quantity": r["available_quantity"],
                    "reserved_quantity": r["reserved_quantity"],
                    "locations_count": len(r["location_count"]),
                    "lots_count": len(r["lot_count"])
                })
        return sorted(enriched, key=lambda x: x["part_code"])

    def get_location_occupancy_report(self):
        return self.loc_service.get_all_locations()
