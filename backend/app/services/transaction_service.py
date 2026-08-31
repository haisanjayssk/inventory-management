from app.repositories.transaction_repository import TransactionRepository
from app.repositories.part_repository import PartRepository, LotRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.cell_repository import CellRepository

class TransactionService:
    def __init__(self):
        self.txn_repo = TransactionRepository()
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()
        self.location_repo = LocationRepository()
        self.user_repo = UserRepository()
        self.cell_repo = CellRepository()

    def get_all_transactions(self, txn_type: str = None, part_id: str = None, lot_id: str = None,
                             location_id: str = None, user_id: str = None, skip: int = 0, limit: int = 50):
        query = {}
        if txn_type:
            query["transaction_type"] = txn_type
        if part_id:
            query["part_id"] = part_id
        if lot_id:
            query["lot_id"] = lot_id
        if user_id:
            query["user_id"] = user_id
        if location_id:
            query["$or"] = [{"from_location_id": location_id}, {"to_location_id": location_id}]

        total_count = self.txn_repo.count(query)
        txns = self.txn_repo.find_all(query, sort_by=[("timestamp", -1)], skip=skip, limit=limit)

        enriched = []
        for t in txns:
            part = self.part_repo.find_by_id(t.get("part_id")) if t.get("part_id") else None
            lot = self.lot_repo.find_by_id(t.get("lot_id")) if t.get("lot_id") else None
            cell = self.cell_repo.find_by_id(t.get("cell_id")) if t.get("cell_id") else None
            f_loc = self.location_repo.find_by_id(t.get("from_location_id")) if t.get("from_location_id") else None
            t_loc = self.location_repo.find_by_id(t.get("to_location_id")) if t.get("to_location_id") else None
            user = self.user_repo.find_by_id(t.get("user_id")) if t.get("user_id") else None

            enriched.append({
                "_id": t["_id"],
                "transaction_type": t.get("transaction_type"),
                "quantity": t.get("quantity"),
                "part_id": t.get("part_id"),
                "part_code": part.get("part_code") if part else None,
                "part_name": part.get("part_name") if part else None,
                "lot_id": t.get("lot_id"),
                "lot_batch_no": lot.get("lot_batch_no") if lot else None,
                "cell_id": t.get("cell_id"),
                "cell_serial_no": cell.get("cell_serial_no") if cell else None,
                "from_location_id": t.get("from_location_id"),
                "from_location_code": f_loc.get("location_code") if f_loc else None,
                "to_location_id": t.get("to_location_id"),
                "to_location_code": t_loc.get("location_code") if t_loc else None,
                "user_id": t.get("user_id"),
                "username": user.get("username") if user else t.get("user_id"),
                "reference_id": t.get("reference_id"),
                "timestamp": t.get("timestamp"),
                "description": t.get("description")
            })

        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "items": enriched
        }

    def get_transaction_by_id(self, txn_id: str):
        t = self.txn_repo.find_by_id(txn_id)
        if not t:
            raise ValueError(f"Transaction {txn_id} not found")
        return t
