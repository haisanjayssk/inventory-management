from app.repositories.cell_repository import CellRepository, CellInventoryRepository
from app.repositories.part_repository import PartRepository, LotRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.transaction_repository import TransactionRepository

class CellService:
    def __init__(self):
        self.cell_repo = CellRepository()
        self.cell_inventory_repo = CellInventoryRepository()
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()
        self.location_repo = LocationRepository()
        self.txn_repo = TransactionRepository()

    def get_all_cells(self, search: str = None, part_id: str = None, lot_id: str = None, location_id: str = None, status: str = None, skip: int = 0, limit: int = 50):
        query = {}
        if search:
            query["cell_serial_no"] = {"$regex": search.strip(), "$options": "i"}
        if part_id:
            query["part_id"] = part_id
        if lot_id:
            query["lot_id"] = lot_id
        if status:
            query["status"] = status

        total_count = self.cell_repo.count(query)
        cells = self.cell_repo.find_all(query, sort_by=[("created_at", -1)], skip=skip, limit=limit)

        enriched_cells = []
        for cell in cells:
            c_id = cell["_id"]
            cinv = self.cell_inventory_repo.find_by_cell_id(c_id)
            loc = self.location_repo.find_by_id(cinv["location_id"]) if cinv else None
            part = self.part_repo.find_by_id(cell.get("part_id"))
            lot = self.lot_repo.find_by_id(cell.get("lot_id"))

            enriched_cells.append({
                "_id": cell["_id"],
                "cell_serial_no": cell["cell_serial_no"],
                "part_id": cell.get("part_id"),
                "part_code": part.get("part_code") if part else None,
                "part_name": part.get("part_name") if part else None,
                "lot_id": cell.get("lot_id"),
                "lot_batch_no": lot.get("lot_batch_no") if lot else None,
                "location_id": loc.get("_id") if loc else None,
                "location_code": loc.get("location_code") if loc else None,
                "nfc_tag_uid": loc.get("nfc_tag_uid") if loc else None,
                "status": cell.get("status", "AVAILABLE"),
                "manufacturing_date": cell.get("manufacturing_date"),
                "date_code": cell.get("date_code"),
                "created_at": cell.get("created_at"),
                "updated_at": cell.get("updated_at")
            })

        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "items": enriched_cells
        }

    def get_cell_by_serial_or_id(self, identifier: str):
        cell = self.cell_repo.find_by_serial(identifier.strip())
        if not cell:
            cell = self.cell_repo.find_by_id(identifier.strip())

        if not cell:
            from app.repositories.inventory_repository import InventoryRepository
            inv_repo = InventoryRepository()
            inv = inv_repo.find_one({"$or": [{"serial_number": identifier.strip()}, {"_id": identifier.strip()}]})
            if inv and inv.get("serial_number"):
                loc = self.location_repo.find_by_id(inv.get("location_id"))
                part = self.part_repo.find_by_id(inv.get("item_id") or inv.get("part_id"))
                txns = self.txn_repo.get_history_for_serial("ORG-001", inv["serial_number"]) if hasattr(self.txn_repo, "get_history_for_serial") else []
                mes_traceability = [
                    {"step": "RECEIVE", "status": "COMPLETED", "timestamp": inv.get("created_at"), "notes": f"Material intake at {loc.get('location_code') if loc else 'Store'}"},
                    {"step": "CDC_TEST", "status": "PENDING", "timestamp": None, "notes": "Capacity, Internal Resistance & OCV Test"},
                    {"step": "GRADING_SORTING", "status": "PENDING", "timestamp": None, "notes": "Cell grouping and bin sorting"},
                    {"step": "MODULE_STACKING", "status": "PENDING", "timestamp": None, "notes": "Laser welding & insulation bracket compression"},
                    {"step": "PACK_INTEGRATION", "status": "PENDING", "timestamp": None, "notes": "BMS wiring and final battery pack build"}
                ]
                return {
                    "cell": {
                        "_id": inv["_id"],
                        "cell_serial_no": inv["serial_number"],
                        "part_id": inv.get("item_id") or inv.get("part_id"),
                        "part_code": part.get("code") or part.get("part_code") if part else None,
                        "part_name": part.get("name") or part.get("part_name") if part else None,
                        "part_attributes": part.get("attributes") if part else {},
                        "lot_id": inv.get("lot_number") or inv.get("lot_id"),
                        "lot_batch_no": inv.get("lot_number") or inv.get("lot_id"),
                        "location": loc,
                        "status": inv.get("status", "AVAILABLE"),
                        "manufacturing_date": inv.get("manufacturing_date"),
                        "date_code": inv.get("date_code"),
                        "created_at": inv.get("created_at"),
                        "updated_at": inv.get("updated_at")
                    },
                    "history": txns,
                    "mes_traceability": mes_traceability
                }

        if not cell:
            raise ValueError(f"Cell '{identifier}' not found")

        c_id = cell["_id"]
        cinv = self.cell_inventory_repo.find_by_cell_id(c_id)
        loc = self.location_repo.find_by_id(cinv["location_id"]) if cinv else None
        part = self.part_repo.find_by_id(cell.get("part_id"))
        lot = self.lot_repo.find_by_id(cell.get("lot_id"))
        txns = self.txn_repo.get_history_for_cell(c_id)

        for txn in txns:
            if txn.get("from_location_id"):
                f_loc = self.location_repo.find_by_id(txn["from_location_id"])
                txn["from_location_code"] = f_loc.get("location_code") if f_loc else None
            if txn.get("to_location_id"):
                t_loc = self.location_repo.find_by_id(txn["to_location_id"])
                txn["to_location_code"] = t_loc.get("location_code") if t_loc else None

        # MES Process History placeholders (Future MES integration ready)
        mes_traceability = [
            {"step": "RECEIVE", "status": "COMPLETED", "timestamp": cell.get("created_at"), "notes": f"Material intake at {loc.get('location_code') if loc else 'Store'}"},
            {"step": "CDC_TEST", "status": "PENDING", "timestamp": None, "notes": "Capacity, Internal Resistance & OCV Test"},
            {"step": "GRADING_SORTING", "status": "PENDING", "timestamp": None, "notes": "Cell grouping and bin sorting"},
            {"step": "MODULE_STACKING", "status": "PENDING", "timestamp": None, "notes": "Laser welding & insulation bracket compression"},
            {"step": "PACK_INTEGRATION", "status": "PENDING", "timestamp": None, "notes": "BMS wiring and final battery pack build"}
        ]

        return {
            "cell": {
                "_id": cell["_id"],
                "cell_serial_no": cell["cell_serial_no"],
                "part_id": cell.get("part_id"),
                "part_code": part.get("part_code") if part else None,
                "part_name": part.get("part_name") if part else None,
                "part_attributes": part.get("attributes") if part else {},
                "lot_id": cell.get("lot_id"),
                "lot_batch_no": lot.get("lot_batch_no") if lot else None,
                "location": loc,
                "status": cell.get("status", "AVAILABLE"),
                "manufacturing_date": cell.get("manufacturing_date"),
                "date_code": cell.get("date_code"),
                "created_at": cell.get("created_at"),
                "updated_at": cell.get("updated_at")
            },
            "history": txns,
            "mes_traceability": mes_traceability
        }
