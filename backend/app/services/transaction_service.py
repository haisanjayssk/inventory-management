from app.repositories.transaction_repository import TransactionRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.user_repository import UserRepository

class TransactionService:
    def __init__(self):
        self.txn_repo = TransactionRepository()
        self.item_repo = ItemRepository()
        self.location_repo = LocationRepository()
        self.user_repo = UserRepository()

    def get_all_transactions(self, org_id: str = "ORG-001", txn_type: str = None, item_id: str = None,
                             location_id: str = None, user_id: str = None, skip: int = 0, limit: int = 50):
        query = {"organization_id": org_id}
        if txn_type:
            query["transaction_type"] = txn_type.upper().strip()
        if item_id:
            query["$or"] = [{"item_id": item_id}, {"part_id": item_id}]
        if user_id:
            query["performed_by"] = user_id
        if location_id:
            query["$or"] = [{"from_location_id": location_id}, {"to_location_id": location_id}]

        total_count = self.txn_repo.count(query)
        txns = self.txn_repo.find_all(query, sort_by=[("timestamp", -1)], skip=skip, limit=limit)

        items_cache = {i["_id"]: i for i in self.item_repo.find_all({"organization_id": org_id})}
        locs_cache = {l["_id"]: l for l in self.location_repo.find_all({"organization_id": org_id})}
        users_cache = {u["_id"]: u for u in self.user_repo.find_all({"organization_id": org_id})}

        enriched = []
        for t in txns:
            item = items_cache.get(t.get("item_id"))
            f_loc = locs_cache.get(t.get("from_location_id"))
            t_loc = locs_cache.get(t.get("to_location_id"))
            user = users_cache.get(t.get("performed_by"))

            enriched.append({
                "_id": t["_id"],
                "t_id": t.get("t_id"),
                "organization_id": t.get("organization_id"),
                "transaction_type": t.get("transaction_type"),
                "quantity": t.get("quantity"),
                "item_id": t.get("item_id"),
                "item_code": item.get("code") if item else None,
                "item_name": item.get("name") if item else None,
                "part_id": t.get("item_id"),
                "part_code": item.get("code") if item else None,
                "part_name": item.get("name") if item else None,
                "lot_number": t.get("lot_number"),
                "lot_batch_no": t.get("lot_number"),
                "serial_number": t.get("serial_number"),
                "cell_serial_no": t.get("serial_number"),
                "from_location_id": t.get("from_location_id"),
                "from_location_code": f_loc.get("location_code") if f_loc else None,
                "to_location_id": t.get("to_location_id"),
                "to_location_code": t_loc.get("location_code") if t_loc else None,
                "vendor_id": t.get("vendor_id"),
                "performed_by": t.get("performed_by"),
                "username": user.get("username") if user else t.get("performed_by"),
                "reference": t.get("reference") or {},
                "reference_id": t.get("reference", {}).get("project_id") or t.get("reference", {}).get("po_number"),
                "timestamp": t.get("timestamp"),
                "remarks": t.get("remarks"),
                "description": t.get("remarks")
            })

        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "items": enriched
        }

    def get_transaction_by_id(self, txn_id: str, org_id: str = "ORG-001"):
        t = self.txn_repo.find_one({"_id": txn_id, "organization_id": org_id})
        if not t:
            t = self.txn_repo.find_by_id(txn_id)
        if not t:
            raise ValueError(f"Transaction '{txn_id}' not found")
        return t
