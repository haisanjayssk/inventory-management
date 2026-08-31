from datetime import datetime, timezone
from app.repositories.part_repository import (
    PartTypeRepository, PartTypeFieldRepository, VendorRepository, PartRepository, LotRepository
)
from app.models.counter import SequenceCounter

class PartService:
    def __init__(self):
        self.part_type_repo = PartTypeRepository()
        self.field_repo = PartTypeFieldRepository()
        self.vendor_repo = VendorRepository()
        self.part_repo = PartRepository()
        self.lot_repo = LotRepository()

    # --- Part Types ---
    def get_all_part_types(self):
        part_types = self.part_type_repo.find_all(sort_by=[("part_type_name", 1)])
        for pt in part_types:
            pt["fields"] = self.field_repo.find_by_part_type(pt["_id"])
        return part_types

    def get_part_type_by_id(self, part_type_id: str):
        pt = self.part_type_repo.find_by_id(part_type_id)
        if not pt:
            raise ValueError(f"Part type {part_type_id} not found")
        pt["fields"] = self.field_repo.find_by_part_type(part_type_id)
        return pt

    def create_part_type(self, data: dict, created_by: str = "admin"):
        name_upper = data["part_type_name"].strip().upper()
        existing = self.part_type_repo.find_one({"part_type_name": name_upper})
        if existing:
            raise ValueError(f"Part type '{name_upper}' already exists")

        pt_id = SequenceCounter.get_next_id("part_type")
        pt_doc = {
            "_id": pt_id,
            "part_type_name": name_upper,
            "description": data.get("description", ""),
            "created_by": created_by
        }
        self.part_type_repo.insert_one(pt_doc)

        fields_list = []
        if "fields" in data and isinstance(data["fields"], list):
            for field in data["fields"]:
                field_doc = self.add_field_to_part_type(pt_id, field)
                fields_list.append(field_doc)

        pt_doc["fields"] = fields_list
        return pt_doc

    def update_part_type(self, part_type_id: str, data: dict):
        pt = self.part_type_repo.find_by_id(part_type_id)
        if not pt:
            raise ValueError(f"Part type {part_type_id} not found")

        update_set = {}
        if "description" in data:
            update_set["description"] = data["description"]
        if "part_type_name" in data:
            update_set["part_type_name"] = data["part_type_name"].strip().upper()

        if update_set:
            self.part_type_repo.update_one({"_id": part_type_id}, {"$set": update_set})

        return self.get_part_type_by_id(part_type_id)

    # --- Part Type Fields (Dynamic Attributes) ---
    def add_field_to_part_type(self, part_type_id: str, field_data: dict):
        key = field_data["field_key"].strip().lower().replace(" ", "_")
        existing = self.field_repo.find_one({"part_type_id": part_type_id, "field_key": key})
        if existing:
            raise ValueError(f"Field key '{key}' already exists for this part type")

        field_id = SequenceCounter.get_next_id("part_type_field")
        doc = {
            "_id": field_id,
            "part_type_id": part_type_id,
            "field_name": field_data["field_name"].strip(),
            "field_key": key,
            "data_type": field_data.get("data_type", "STRING").upper(),
            "unit": field_data.get("unit"),
            "options": field_data.get("options", []),
            "required": bool(field_data.get("required", False)),
            "active": True
        }
        self.field_repo.insert_one(doc)
        return doc

    def delete_field(self, field_id: str):
        return self.field_repo.delete_one({"_id": field_id})

    # --- Vendors ---
    def get_all_vendors(self):
        return self.vendor_repo.find_all(sort_by=[("vendor_name", 1)])

    def get_vendor_by_id(self, vendor_id: str):
        v = self.vendor_repo.find_by_id(vendor_id)
        if not v:
            raise ValueError(f"Vendor {vendor_id} not found")
        return v

    def create_vendor(self, data: dict):
        existing = self.vendor_repo.find_one({"vendor_name": data["vendor_name"].strip()})
        if existing:
            raise ValueError(f"Vendor '{data['vendor_name']}' already exists")

        vendor_id = SequenceCounter.get_next_id("vendor")
        doc = {
            "_id": vendor_id,
            "vendor_name": data["vendor_name"].strip(),
            "contact": data.get("contact", ""),
            "email": data.get("email"),
            "address": data.get("address", ""),
            "country": data.get("country", "India"),
            "status": data.get("status", "ACTIVE")
        }
        self.vendor_repo.insert_one(doc)
        return doc

    def update_vendor(self, vendor_id: str, data: dict):
        v = self.vendor_repo.find_by_id(vendor_id)
        if not v:
            raise ValueError(f"Vendor {vendor_id} not found")
        self.vendor_repo.update_one({"_id": vendor_id}, {"$set": data})
        return self.get_vendor_by_id(vendor_id)

    # --- Parts ---
    def get_all_parts(self, search: str = None, part_type_id: str = None, vendor_id: str = None, tracking_type: str = None):
        query = {}
        if part_type_id:
            query["part_type_id"] = part_type_id
        if vendor_id:
            query["vendor_id"] = vendor_id
        if tracking_type:
            query["tracking_type"] = tracking_type
        if search:
            query["$or"] = [
                {"part_code": {"$regex": search, "$options": "i"}},
                {"part_name": {"$regex": search, "$options": "i"}},
                {"mpn": {"$regex": search, "$options": "i"}},
                {"mfr": {"$regex": search, "$options": "i"}}
            ]

        parts = self.part_repo.find_all(query, sort_by=[("part_code", 1)])
        # Populate vendor name and part type name
        for p in parts:
            if p.get("vendor_id"):
                v = self.vendor_repo.find_by_id(p["vendor_id"])
                p["vendor_name"] = v["vendor_name"] if v else None
            if p.get("part_type_id"):
                pt = self.part_type_repo.find_by_id(p["part_type_id"])
                p["part_type_name"] = pt["part_type_name"] if pt else None
        return parts

    def get_part_by_id(self, part_id: str):
        p = self.part_repo.find_by_id(part_id)
        if not p:
            raise ValueError(f"Part {part_id} not found")
        if p.get("vendor_id"):
            v = self.vendor_repo.find_by_id(p["vendor_id"])
            p["vendor_name"] = v["vendor_name"] if v else None
        if p.get("part_type_id"):
            pt = self.part_type_repo.find_by_id(p["part_type_id"])
            p["part_type_name"] = pt["part_type_name"] if pt else None
            p["configured_fields"] = self.field_repo.find_by_part_type(p["part_type_id"])
        return p

    def create_part(self, data: dict):
        # Validate part code uniqueness
        part_code = data["part_code"].strip()
        if self.part_repo.find_by_code(part_code):
            raise ValueError(f"Part code '{part_code}' already exists")

        # Validate Part Type
        pt = self.part_type_repo.find_by_id(data["part_type_id"])
        if not pt:
            raise ValueError(f"Part type '{data['part_type_id']}' does not exist")

        # Validate Vendor if provided
        if data.get("vendor_id"):
            v = self.vendor_repo.find_by_id(data["vendor_id"])
            if not v:
                raise ValueError(f"Vendor '{data['vendor_id']}' does not exist")

        # Validate required dynamic fields
        configured_fields = self.field_repo.find_by_part_type(data["part_type_id"])
        attributes = data.get("attributes", {}) or {}
        for f in configured_fields:
            if f.get("required") and f["field_key"] not in attributes:
                raise ValueError(f"Attribute '{f['field_name']}' ({f['field_key']}) is required for part type '{pt['part_type_name']}'")

        part_id = SequenceCounter.get_next_id("part")
        part_doc = {
            "_id": part_id,
            "part_type_id": data["part_type_id"],
            "part_code": part_code,
            "part_name": data["part_name"].strip(),
            "package": data.get("package", ""),
            "vendor_id": data.get("vendor_id"),
            "description": data.get("description", ""),
            "mfr": data.get("mfr", ""),
            "mpn": data.get("mpn", ""),
            "rohs": data.get("rohs", "YES"),
            "static_sensitive": data.get("static_sensitive", "NO"),
            "msl": data.get("msl", "NA"),
            "unit_of_measure": data.get("unit_of_measure", "PCS"),
            "tracking_type": data.get("tracking_type", "QUANTITY"),
            "attributes": attributes,
            "active": data.get("active", True)
        }
        self.part_repo.insert_one(part_doc)
        return self.get_part_by_id(part_id)

    def update_part(self, part_id: str, data: dict):
        p = self.part_repo.find_by_id(part_id)
        if not p:
            raise ValueError(f"Part {part_id} not found")

        # Prohibit changing tracking_type or part_code if already in use
        update_data = {k: v for k, v in data.items() if k not in ["_id", "created_at"]}
        self.part_repo.update_one({"_id": part_id}, {"$set": update_data})
        return self.get_part_by_id(part_id)

    def delete_part(self, part_id: str):
        # Soft delete / toggle active
        return self.part_repo.update_one({"_id": part_id}, {"$set": {"active": False}})

    # --- Lots ---
    def get_all_lots(self, part_id: str = None):
        query = {"part_id": part_id} if part_id else {}
        lots = self.lot_repo.find_all(query, sort_by=[("created_at", -1)])
        for lot in lots:
            if lot.get("part_id"):
                p = self.part_repo.find_by_id(lot["part_id"])
                lot["part_code"] = p["part_code"] if p else None
                lot["part_name"] = p["part_name"] if p else None
            if lot.get("vendor_id"):
                v = self.vendor_repo.find_by_id(lot["vendor_id"])
                lot["vendor_name"] = v["vendor_name"] if v else None
        return lots

    def get_lot_by_id(self, lot_id: str):
        lot = self.lot_repo.find_by_id(lot_id)
        if not lot:
            raise ValueError(f"Lot {lot_id} not found")
        if lot.get("part_id"):
            p = self.part_repo.find_by_id(lot["part_id"])
            lot["part_code"] = p["part_code"] if p else None
            lot["part_name"] = p["part_name"] if p else None
        if lot.get("vendor_id"):
            v = self.vendor_repo.find_by_id(lot["vendor_id"])
            lot["vendor_name"] = v["vendor_name"] if v else None
        return lot

    def create_lot(self, data: dict, session=None):
        part = self.part_repo.find_by_id(data["part_id"], session=session)
        if not part:
            raise ValueError(f"Part {data['part_id']} does not exist")

        batch_no = data["lot_batch_no"].strip()
        existing = self.lot_repo.find_by_part_and_batch(data["part_id"], batch_no, session=session)
        if existing:
            return existing

        lot_id = SequenceCounter.get_next_id("lot", session=session)
        doc = {
            "_id": lot_id,
            "part_id": data["part_id"],
            "lot_batch_no": batch_no,
            "vendor_id": data.get("vendor_id") or part.get("vendor_id"),
            "dop": data.get("dop"),
            "manufacturing_date": data.get("manufacturing_date"),
            "received_date": data.get("received_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "expiry_date": data.get("expiry_date")
        }
        self.lot_repo.insert_one(doc, session=session)
        return doc
