from app.config.database import Database
from app.repositories.part_repository import PartRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.cell_repository import CellRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.transaction_service import TransactionService

class DashboardService:
    def __init__(self):
        self.part_repo = PartRepository()
        self.location_repo = LocationRepository()
        self.inv_repo = InventoryRepository()
        self.cell_repo = CellRepository()
        self.txn_service = TransactionService()

    def get_metrics(self):
        db = Database.get_db()
        
        # 1. Parts count
        total_parts = self.part_repo.count()

        # 2. Stock aggregations
        stock_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_quantity": {"$sum": "$quantity"},
                    "total_available": {"$sum": "$available_quantity"},
                    "total_reserved": {"$sum": "$reserved_quantity"}
                }
            }
        ]
        stock_agg = list(db.inventory.aggregate(stock_pipeline))
        total_stock = stock_agg[0]["total_quantity"] if stock_agg else 0
        total_available = stock_agg[0]["total_available"] if stock_agg else 0
        total_reserved = stock_agg[0]["total_reserved"] if stock_agg else 0

        # 3. Cells metrics
        total_cells = self.cell_repo.count()
        cell_status_counts = {}
        for c in db.cells.aggregate([{"$group": {"_id": "$status", "count": {"$sum": 1}}}]):
            cell_status_counts[c["_id"]] = c["count"]

        # 4. Locations metrics
        total_locations = self.location_repo.count()
        active_locations = self.location_repo.count({"status": "ACTIVE"})

        # Occupied locations count (locations with inventory qty > 0 or cells assigned)
        occupied_loc_ids = set(db.inventory.distinct("location_id", {"quantity": {"$gt": 0}}))
        occupied_loc_ids.update(db.cell_inventory.distinct("location_id"))
        occupied_count = len(occupied_loc_ids)
        empty_count = max(0, total_locations - occupied_count)

        # 5. Low stock alerts (items where available_quantity < 500)
        low_stock_items = []
        low_stock_docs = self.inv_repo.find_all(
            {"available_quantity": {"$lte": 500}, "quantity": {"$gt": 0}},
            limit=10
        )
        for doc in low_stock_docs:
            part = self.part_repo.find_by_id(doc.get("part_id"))
            if part:
                low_stock_items.append({
                    "part_code": part.get("part_code"),
                    "part_name": part.get("part_name"),
                    "available_quantity": doc.get("available_quantity"),
                    "unit": part.get("unit_of_measure", "PCS")
                })

        # 6. Recent transactions
        recent_txns = self.txn_service.get_all_transactions(limit=10)["items"]

        # 7. Stock movement summary (Received vs Issued)
        receive_count = db.transactions.count_documents({"transaction_type": "RECEIVE"})
        issue_count = db.transactions.count_documents({"transaction_type": "ISSUE"})
        transfer_count = db.transactions.count_documents({"transaction_type": "TRANSFER"})

        return {
            "summary": {
                "total_parts": total_parts,
                "total_stock_quantity": total_stock,
                "total_available_quantity": total_available,
                "total_reserved_quantity": total_reserved,
                "total_cells": total_cells,
                "total_locations": total_locations,
                "active_locations": active_locations,
                "occupied_locations": occupied_count,
                "empty_locations": empty_count,
                "occupancy_rate": round((occupied_count / total_locations * 100) if total_locations > 0 else 0, 1)
            },
            "cell_status_summary": cell_status_counts,
            "movement_counts": {
                "receive": receive_count,
                "issue": issue_count,
                "transfer": transfer_count
            },
            "low_stock_alerts": low_stock_items,
            "recent_transactions": recent_txns
        }
