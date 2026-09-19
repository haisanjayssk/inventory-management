from app.config.database import Database
from app.repositories.item_repository import ItemRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.transaction_repository import TransactionRepository

class DashboardService:
    def __init__(self):
        self.item_repo = ItemRepository()
        self.location_repo = LocationRepository()
        self.inv_repo = InventoryRepository()
        self.txn_repo = TransactionRepository()

    def get_metrics(self, org_id: str = "ORG-001"):
        db = Database.get_db()
        
        # 1. Items count
        total_parts = self.item_repo.count({"organization_id": org_id})

        # 2. Stock aggregations
        stock_pipeline = [
            {"$match": {"organization_id": org_id, "status": "AVAILABLE"}},
            {
                "$group": {
                    "_id": None,
                    "total_quantity": {"$sum": "$quantity"}
                }
            }
        ]
        stock_agg = list(db.inventory.aggregate(stock_pipeline))
        total_stock = stock_agg[0]["total_quantity"] if stock_agg else 0

        # 3. Cells metrics
        total_cells = db.inventory.count_documents({
            "organization_id": org_id,
            "serial_number": {"$ne": None},
            "status": "AVAILABLE"
        })

        # 4. Locations metrics
        total_locations = self.location_repo.count({"organization_id": org_id})
        active_locations = self.location_repo.count({"organization_id": org_id, "status": "ACTIVE"})

        occupied_loc_ids = set(db.inventory.distinct("location_id", {"organization_id": org_id, "quantity": {"$gt": 0}, "status": "AVAILABLE"}))
        occupied_count = len(occupied_loc_ids)
        empty_count = max(0, total_locations - occupied_count)

        # 5. Low stock alerts
        low_stock_items = []
        low_docs = db.inventory.find(
            {"organization_id": org_id, "serial_number": None, "quantity": {"$lte": 500, "$gt": 0}},
            limit=10
        )
        for doc in low_docs:
            item = self.item_repo.find_one({"_id": doc.get("item_id"), "organization_id": org_id})
            if item:
                low_stock_items.append({
                    "part_code": item.get("code"),
                    "part_name": item.get("name"),
                    "available_quantity": doc.get("quantity"),
                    "unit": "PCS"
                })

        # 6. Recent transactions
        recent_txns = list(db.inventory_transactions.find({"organization_id": org_id}).sort("timestamp", -1).limit(10))

        # 7. Stock movement breakdown
        receive_count = db.inventory_transactions.count_documents({"organization_id": org_id, "transaction_type": "RECEIVE"})
        issue_count = db.inventory_transactions.count_documents({"organization_id": org_id, "transaction_type": "ISSUE"})
        transfer_count = db.inventory_transactions.count_documents({"organization_id": org_id, "transaction_type": "TRANSFER"})

        return {
            "summary": {
                "total_parts": total_parts,
                "total_stock_quantity": total_stock,
                "total_available_quantity": total_stock,
                "total_reserved_quantity": 0,
                "total_cells": total_cells,
                "total_locations": total_locations,
                "active_locations": active_locations,
                "occupied_locations": occupied_count,
                "empty_locations": empty_count,
                "occupancy_rate": round((occupied_count / total_locations * 100) if total_locations > 0 else 0, 1)
            },
            "movement_counts": {
                "receive": receive_count,
                "issue": issue_count,
                "transfer": transfer_count
            },
            "low_stock_alerts": low_stock_items,
            "recent_transactions": recent_txns
        }
