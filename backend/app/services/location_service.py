from datetime import datetime, timezone
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.cell_repository import CellInventoryRepository
from app.repositories.part_repository import PartRepository, LotRepository
from app.models.counter import SequenceCounter

class LocationService:
    def __init__(self):
        self.location_repo = LocationRepository()
        self.inventory_repo = InventoryRepository()
        self.cell_inventory_repo = CellInventoryRepository()
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()

    def _enrich_inventory(self, loc_id: str):
        items = self.inventory_repo.find_by_location(loc_id)
        enriched = []
        for inv in items:
            part = self.part_repo.find_by_id(inv.get("part_id"))
            lot = self.lot_repo.find_by_id(inv.get("lot_id"))
            enriched.append({
                **inv,
                "part_code": part.get("part_code") if part else None,
                "part_name": part.get("part_name") if part else None,
                "unit_of_measure": part.get("unit_of_measure", "PCS") if part else "PCS",
                "lot_batch_no": lot.get("lot_batch_no") if lot else None
            })
        return enriched

    def generate_warehouse_code(self, warehouse_name: str) -> str:
        """Derives a unique warehouse code prefix, e.g. EMS -> E, MES -> ME."""
        clean_name = warehouse_name.strip().upper()
        # Find existing warehouse codes
        existing_locations = self.location_repo.find_all()
        existing_wh_codes = {loc.get("warehouse_code") for loc in existing_locations if loc.get("warehouse_code")}

        # Try 1 letter, then 2, then 3
        for length in range(1, len(clean_name) + 1):
            candidate = clean_name[:length]
            if candidate not in existing_wh_codes:
                return candidate
        return clean_name[:3]

    def build_location_code(self, warehouse_code: str, bay: str, row: int, rack: int, section: str) -> str:
        """Builds standard location code like E11-1A."""
        return f"{warehouse_code}{bay}{row}-{rack}{section}"

    def get_all_locations(self, warehouse_code: str = None, status: str = None):
        query = {}
        if warehouse_code:
            query["warehouse_code"] = warehouse_code
        if status:
            query["status"] = status

        locations = self.location_repo.find_all(query, sort_by=[("location_code", 1)])
        # Annotate occupancy info
        for loc in locations:
            loc_id = loc["_id"]
            qty_inv = self.inventory_repo.find_by_location(loc_id)
            cell_inv = self.cell_inventory_repo.find_by_location_id(loc_id)
            total_items = sum(item.get("quantity", 0) for item in qty_inv) + len(cell_inv)
            loc["total_items"] = total_items
            loc["is_occupied"] = total_items > 0
        return locations

    def get_location_by_id(self, location_id: str):
        loc = self.location_repo.find_by_id(location_id)
        if not loc:
            raise ValueError(f"Location {location_id} not found")
        loc_id = loc["_id"]
        loc["inventory"] = self._enrich_inventory(loc_id)
        loc["cells"] = self.cell_inventory_repo.find_by_location_id(loc_id)
        return loc

    def resolve_by_code(self, location_code: str):
        loc = self.location_repo.find_by_code(location_code.strip())
        if not loc:
            raise ValueError(f"Location with code '{location_code}' not found")
        loc_id = loc["_id"]
        loc["inventory"] = self._enrich_inventory(loc_id)
        loc["cells"] = self.cell_inventory_repo.find_by_location_id(loc_id)
        return loc

    def resolve_by_nfc(self, nfc_tag_uid: str):
        cleaned_uid = nfc_tag_uid.strip()
        loc = self.location_repo.find_by_nfc(cleaned_uid)
        if not loc:
            raise ValueError(f"No location registered with NFC UID: '{nfc_tag_uid}'")
        loc_id = loc["_id"]
        loc["inventory"] = self._enrich_inventory(loc_id)
        loc["cells"] = self.cell_inventory_repo.find_by_location_id(loc_id)
        return loc

    def create_location(self, data: dict):
        wh_code = data["warehouse_code"].strip().upper()
        bay = str(data["bay_number"]).strip()
        row = int(data["row_number"])
        rack = int(data["rack_number"])
        section = str(data["section_code"]).strip().upper()

        loc_code = data.get("location_code") or self.build_location_code(wh_code, bay, row, rack, section)
        if self.location_repo.find_by_code(loc_code):
            raise ValueError(f"Location code '{loc_code}' already exists")

        nfc_uid = data.get("nfc_tag_uid") or f"inventory://location/{loc_code}"
        if self.location_repo.find_by_nfc(nfc_uid):
            raise ValueError(f"NFC Tag UID '{nfc_uid}' is already mapped to another location")

        loc_id = SequenceCounter.get_next_id("location")
        loc_doc = {
            "_id": loc_id,
            "location_code": loc_code,
            "warehouse_code": wh_code,
            "bay_number": bay,
            "row_number": row,
            "rack_number": rack,
            "section_code": section,
            "nfc_tag_uid": nfc_uid,
            "status": data.get("status", "ACTIVE")
        }
        self.location_repo.insert_one(loc_doc)
        return loc_doc

    def bulk_generate_locations(self, data: dict):
        wh_name = data["warehouse_name"].strip()
        wh_code = (data.get("warehouse_code") or self.generate_warehouse_code(wh_name)).upper()
        racks_count = int(data["racks_count"])
        sections = data["sections"] # e.g. ["A", "B", "C"]

        # Support both custom bay configs and uniform bays
        bay_configs = data.get("bay_configs")
        if not bay_configs:
            bays = data.get("bays") or []
            rows_count = int(data.get("rows_count") or 1)
            bay_configs = [{"bay": str(b).strip(), "rows_count": rows_count} for b in bays if str(b).strip()]

        if not bay_configs:
            raise ValueError("At least one bay configuration must be provided")

        total_to_generate = sum(
            int(cfg["rows_count"]) * racks_count * len(sections)
            for cfg in bay_configs
        )
        if total_to_generate > 2000:
            raise ValueError(f"Bulk generation exceeds limit of 2,000 locations per batch (attempted {total_to_generate})")

        location_ids = SequenceCounter.get_next_batch_ids("location", total_to_generate)
        id_idx = 0

        created_docs = []
        now = datetime.now(timezone.utc).isoformat()

        for cfg in bay_configs:
            bay = str(cfg["bay"]).strip()
            rows_for_bay = int(cfg["rows_count"])
            for row in range(1, rows_for_bay + 1):
                for rack in range(1, racks_count + 1):
                    for section in sections:
                        loc_code = self.build_location_code(wh_code, bay, row, rack, str(section).upper())
                        
                        # Skip if already exists
                        if self.location_repo.find_by_code(loc_code):
                            continue

                        doc = {
                            "_id": location_ids[id_idx],
                            "location_code": loc_code,
                            "warehouse_name": wh_name,
                            "warehouse_code": wh_code,
                            "bay_number": bay,
                            "row_number": row,
                            "rack_number": rack,
                            "section_code": str(section).upper(),
                            "nfc_tag_uid": f"inventory://location/{loc_code}",
                            "status": "ACTIVE",
                            "created_at": now,
                            "updated_at": now
                        }
                        id_idx += 1
                        created_docs.append(doc)

        if created_docs:
            self.location_repo.insert_many(created_docs)

        return {
            "warehouse_code": wh_code,
            "generated_count": len(created_docs),
            "locations": created_docs[:100] # preview first 100
        }

    def update_location(self, location_id: str, data: dict):
        loc = self.location_repo.find_by_id(location_id)
        if not loc:
            raise ValueError(f"Location {location_id} not found")

        update_set = {}
        if "status" in data:
            update_set["status"] = data["status"]
        if "nfc_tag_uid" in data:
            update_set["nfc_tag_uid"] = data["nfc_tag_uid"]

        if update_set:
            self.location_repo.update_one({"_id": location_id}, {"$set": update_set})
        return self.get_location_by_id(location_id)
