from datetime import datetime, timezone
from app.repositories.location_repository import LocationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.item_repository import ItemRepository
from app.models.counter import SequenceCounter

class LocationService:
    def __init__(self):
        self.location_repo = LocationRepository()
        self.inventory_repo = InventoryRepository()
        self.item_repo = ItemRepository()

    def _enrich_inventory(self, loc_id: str, org_id: str = "ORG-001"):
        items = self.inventory_repo.find_by_location(org_id, loc_id)
        enriched = []
        for inv in items:
            item = self.item_repo.find_one({"_id": inv.get("item_id"), "organization_id": org_id})
            enriched.append({
                **inv,
                "part_id": inv.get("item_id"),
                "item_code": item.get("code") if item else None,
                "part_code": item.get("code") if item else None,
                "part_name": item.get("name") if item else None,
                "lot_batch_no": inv.get("lot_number"),
                "available_quantity": inv.get("quantity", 0)
            })
        return enriched

    def get_warehouses(self, org_id: str = "ORG-001"):
        locations = self.location_repo.find_all_by_org(org_id)
        wh_map = {}
        for loc in locations:
            code = loc.get("warehouse_code") or (loc.get("location_code", "")[3:] if loc.get("location_code", "").startswith("WH-") else loc.get("location_code", "")[:1])
            if not code:
                continue
            name = loc.get("warehouse_name") or (loc.get("name") if loc.get("type") == "WAREHOUSE" else None) or f"Warehouse {code}"
            if code not in wh_map:
                wh_map[code] = {
                    "warehouse_code": code,
                    "warehouse_name": name,
                    "total_bins": 0,
                    "occupied_bins": 0,
                    "bays": set(),
                }
            elif name and wh_map[code]["warehouse_name"] == f"Warehouse {code}":
                wh_map[code]["warehouse_name"] = name

            if loc.get("type") != "WAREHOUSE":
                wh_map[code]["total_bins"] += 1
                if loc.get("bay_number"):
                    wh_map[code]["bays"].add(str(loc.get("bay_number")))
                inv_items = self.inventory_repo.find_by_location(org_id, loc["_id"])
                if sum(item.get("quantity", 0) for item in inv_items) > 0:
                    wh_map[code]["occupied_bins"] += 1

        result = []
        for code, data in wh_map.items():
            result.append({
                "warehouse_code": data["warehouse_code"],
                "warehouse_name": data["warehouse_name"],
                "total_bins": data["total_bins"],
                "occupied_bins": data["occupied_bins"],
                "total_bays": len(data["bays"]),
                "bays": sorted(list(data["bays"]))
            })

        return sorted(result, key=lambda w: w["warehouse_code"])

    def get_all_locations(self, org_id: str = "ORG-001", warehouse_code: str = None, status: str = None, loc_type: str = None):
        query = {"organization_id": org_id}
        if warehouse_code:
            query["warehouse_code"] = warehouse_code
        if status:
            query["status"] = status
        if loc_type:
            query["type"] = loc_type.upper()

        locations = self.location_repo.find_all(query, sort_by=[("location_code", 1)])
        # Annotate occupancy
        for loc in locations:
            loc_id = loc["_id"]
            items = self.inventory_repo.find_by_location(org_id, loc_id)
            total_items = sum(item.get("quantity", 0) for item in items)
            loc["total_items"] = total_items
            loc["is_occupied"] = total_items > 0
            loc["inventory"] = items
        return locations

    def get_location_tree(self, org_id: str = "ORG-001"):
        """Builds hierarchical tree structure of locations."""
        locations = self.get_all_locations(org_id)
        lookup = {l["location_code"]: {**l, "children": []} for l in locations}
        roots = []

        for loc in locations:
            code = loc["location_code"]
            node = lookup[code]
            parent_code = loc.get("parent_id")
            if parent_code and parent_code in lookup:
                lookup[parent_code]["children"].append(node)
            else:
                roots.append(node)

        return roots

    def get_location_by_id(self, location_id: str, org_id: str = "ORG-001"):
        loc = self.location_repo.find_one({"_id": location_id, "organization_id": org_id})
        if not loc:
            loc = self.location_repo.find_by_code(org_id, location_id)
        if not loc:
            raise ValueError(f"Location '{location_id}' not found")
        loc_id = loc["_id"]
        loc["inventory"] = self._enrich_inventory(loc_id, org_id)
        loc["cells"] = [i for i in loc["inventory"] if i.get("serial_number")]
        return loc

    def resolve_by_code(self, location_code: str, org_id: str = "ORG-001"):
        loc = self.location_repo.find_by_code(org_id, location_code.strip())
        if not loc:
            raise ValueError(f"Location with code '{location_code}' not found")
        return self.get_location_by_id(loc["_id"], org_id)

    def resolve_by_nfc(self, nfc_uid: str, org_id: str = "ORG-001"):
        loc = self.location_repo.find_by_nfc(org_id, nfc_uid.strip())
        if not loc:
            raise ValueError(f"No location matched with NFC Tag '{nfc_uid}'")
        return self.get_location_by_id(loc["_id"], org_id)

    def resolve_by_qr(self, qr_code: str, org_id: str = "ORG-001"):
        loc = self.location_repo.find_by_qr(org_id, qr_code.strip())
        if not loc:
            raise ValueError(f"No location matched with QR Code '{qr_code}'")
        return self.get_location_by_id(loc["_id"], org_id)

    def create_location(self, data: dict, org_id: str = "ORG-001"):
        code = data["location_code"].strip().upper()
        if self.location_repo.find_by_code(org_id, code):
            raise ValueError(f"Location code '{code}' already exists")

        nfc_uid = data.get("nfc_uid") or data.get("nfc_tag_uid") or f"inventory://location/{code}"
        qr_code = data.get("qr_code") or f"QR-{code}"

        loc_id = SequenceCounter.get_next_id("location")
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "_id": loc_id,
            "organization_id": org_id,
            "location_code": code,
            "name": data.get("name") or f"Location {code}",
            "type": (data.get("type") or "BIN").upper(),
            "parent_id": data.get("parent_id"),
            "site_id": data.get("site_id", "SITE-001"),
            "nfc_uid": nfc_uid,
            "nfc_tag_uid": nfc_uid,
            "qr_code": qr_code,
            "warehouse_code": data.get("warehouse_code"),
            "bay_number": data.get("bay_number"),
            "row_number": data.get("row_number"),
            "rack_number": data.get("rack_number"),
            "section_code": data.get("section_code"),
            "status": data.get("status", "ACTIVE"),
            "created_at": now,
            "updated_at": now
        }
        self.location_repo.insert_one(doc)
        return doc

    def bulk_generate_locations(self, data: dict, org_id: str = "ORG-001", site_id: str = "SITE-001"):
        effective_site = data.get("site_id") or site_id
        wh_name = data["warehouse_name"].strip()
        wh_code = (data.get("warehouse_code") or wh_name[:1]).upper().strip()
        racks_count = int(data["racks_count"])
        sections = data.get("sections") or []
        sections_to_use = [s.strip().upper() for s in sections if s.strip()] or [""]

        bay_rows = []
        if data.get("bay_configs"):
            for cfg in data["bay_configs"]:
                bay_rows.append((str(cfg["bay"]).strip(), int(cfg["rows_count"])))
        else:
            bays = data.get("bays") or ["1", "2", "3"]
            rows_cnt = int(data.get("rows_count", 2))
            for b in bays:
                bay_rows.append((str(b).strip(), rows_cnt))

        # Ensure parent warehouse exists
        wh_loc = self.location_repo.find_by_code(org_id, f"WH-{wh_code}")
        if not wh_loc:
            wh_loc = self.create_location({
                "location_code": f"WH-{wh_code}",
                "name": wh_name,
                "type": "WAREHOUSE",
                "warehouse_code": wh_code,
                "status": "ACTIVE"
            }, org_id=org_id)

        docs = []
        codes_to_create = []
        for bay, rows_count in bay_rows:
            for row in range(1, rows_count + 1):
                for rack in range(1, racks_count + 1):
                    for sec in sections_to_use:
                        sec_str = sec if sec else ""
                        loc_code = f"{wh_code}{bay}{row}-{rack}{sec_str}"
                        codes_to_create.append((loc_code, bay, row, rack, sec_str))

        existing = {l["location_code"] for l in self.location_repo.find_all_by_org(org_id)}
        new_codes = [c for c in codes_to_create if c[0] not in existing]

        if new_codes:
            batch_ids = SequenceCounter.get_next_batch_ids("location", len(new_codes))
            now = datetime.now(timezone.utc).isoformat()
            for idx, (loc_code, bay, row, rack, sec_str) in enumerate(new_codes):
                docs.append({
                    "_id": batch_ids[idx],
                    "organization_id": org_id,
                    "location_code": loc_code,
                    "name": f"Bin {loc_code}",
                    "type": "BIN",
                    "parent_id": f"WH-{wh_code}",
                    "site_id": data.get("site_id", "SITE-001"),
                    "warehouse_code": wh_code,
                    "warehouse_name": wh_name,
                    "bay_number": str(bay),
                    "row_number": str(row),
                    "rack_number": str(rack),
                    "section_code": sec_str if sec_str else None,
                    "nfc_uid": f"inventory://location/{loc_code}",
                    "nfc_tag_uid": f"inventory://location/{loc_code}",
                    "qr_code": f"QR-{loc_code}",
                    "status": "ACTIVE",
                    "created_at": now,
                    "updated_at": now
                })
            self.location_repo.insert_many(docs)

        return {
            "created_count": len(docs),
            "generated_count": len(docs),
            "warehouse_code": wh_code,
            "warehouse_name": wh_name,
            "locations": docs,
            "message": f"Successfully generated {len(docs)} storage locations"
        }

    def update_location(self, location_id: str, data: dict, org_id: str = "ORG-001"):
        loc = self.get_location_by_id(location_id, org_id)
        update_data = {k: v for k, v in data.items() if k not in ["_id", "organization_id", "location_code", "created_at"]}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.location_repo.update_one({"_id": loc["_id"]}, {"$set": update_data})
        return self.get_location_by_id(loc["_id"], org_id)
