import io
import csv
import json
from datetime import datetime, timezone
from pymongo import InsertOne, UpdateOne

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    openpyxl = None
    OPENPYXL_AVAILABLE = False

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
        part_types = self.part_type_repo.find_all(sort_by=[("code", 1)])
        for pt in part_types:
            pt_name = pt.get("part_type_name") or pt.get("name") or pt.get("code")
            pt["part_type_name"] = pt.get("code") or pt_name
            pt["name"] = pt.get("name") or pt_name
            pt["code"] = pt.get("code") or pt_name
            fields = pt.get("fields") or self.field_repo.find_by_part_type(pt["_id"])
            pt["fields"] = fields
        return part_types

    def get_part_type_by_id(self, part_type_id: str):
        pt = self.part_type_repo.find_by_id(part_type_id)
        if not pt:
            pt = self.part_type_repo.find_one({"code": part_type_id.strip().upper()})
        if not pt:
            pt = self.part_type_repo.find_one({"part_type_name": part_type_id.strip().upper()})
        if not pt:
            raise ValueError(f"Part type {part_type_id} not found")
        pt["part_type_name"] = pt.get("code") or pt.get("name") or pt.get("part_type_name")
        pt["name"] = pt.get("name") or pt["part_type_name"]
        pt["fields"] = pt.get("fields") or self.field_repo.find_by_part_type(part_type_id)
        return pt

    def create_part_type(self, data: dict, created_by: str = "admin"):
        name_upper = (data.get("part_type_name") or data.get("name") or data.get("code", "")).strip().upper()
        existing = self.part_type_repo.find_one({
            "$or": [
                {"part_type_name": name_upper},
                {"code": name_upper},
                {"name": name_upper}
            ]
        })
        if existing:
            raise ValueError(f"Part type '{name_upper}' already exists")

        pt_id = SequenceCounter.get_next_id("part_type")
        pt_doc = {
            "_id": pt_id,
            "organization_id": "ORG-001",
            "code": name_upper,
            "name": data.get("name", name_upper),
            "part_type_name": name_upper,
            "description": data.get("description", ""),
            "tracking_mode": data.get("tracking_mode", "QUANTITY"),
            "tracking_type": data.get("tracking_mode", "QUANTITY"),
            "fields": data.get("fields", []),
            "created_by": created_by
        }
        self.part_type_repo.insert_one(pt_doc)

        fields_list = []
        if "fields" in data and isinstance(data["fields"], list):
            for field in data["fields"]:
                field_doc = self.add_field_to_part_type(pt_id, field)
                fields_list.append(field_doc)

        pt_doc["fields"] = fields_list or data.get("fields", [])
        return pt_doc

    def update_part_type(self, part_type_id: str, data: dict):
        pt = self.get_part_type_by_id(part_type_id)
        update_set = {}
        if "description" in data:
            update_set["description"] = data["description"]
        if "part_type_name" in data:
            name_upper = data["part_type_name"].strip().upper()
            update_set["part_type_name"] = name_upper
            update_set["code"] = name_upper
            update_set["name"] = data["part_type_name"].strip()

        if update_set:
            self.part_type_repo.update_one({"_id": pt["_id"]}, {"$set": update_set})

        return self.get_part_type_by_id(pt["_id"])

    # --- Part Type Fields (Dynamic Attributes) ---
    def add_field_to_part_type(self, part_type_id: str, field_data: dict):
        key = (field_data.get("field_key") or field_data.get("key") or field_data.get("field_name") or field_data.get("name", "")).strip().lower().replace(" ", "_")
        existing = self.field_repo.find_one({"part_type_id": part_type_id, "$or": [{"field_key": key}, {"key": key}]})
        if existing:
            raise ValueError(f"Field key '{key}' already exists for this part type")

        field_id = SequenceCounter.get_next_id("part_type_field")
        f_name = (field_data.get("field_name") or field_data.get("name") or key).strip()
        doc = {
            "_id": field_id,
            "part_type_id": part_type_id,
            "field_name": f_name,
            "field_key": key,
            "name": f_name,
            "key": key,
            "data_type": (field_data.get("data_type") or field_data.get("type") or "STRING").upper(),
            "unit": field_data.get("unit"),
            "options": field_data.get("options", []),
            "required": field_data.get("required", False),
            "active": field_data.get("active", True)
        }
        self.field_repo.insert_one(doc)
        return doc

    def delete_field(self, field_id: str):
        return self.field_repo.delete_one({"_id": field_id})

    # --- Vendors ---
    def get_all_vendors(self):
        vendors = self.vendor_repo.find_all(sort_by=[("name", 1)])
        for v in vendors:
            v["vendor_name"] = v.get("name") or v.get("vendor_name")
        return vendors

    def get_vendor_by_id(self, vendor_id: str):
        v = self.vendor_repo.find_by_id(vendor_id)
        if not v:
            raise ValueError(f"Vendor {vendor_id} not found")
        v["vendor_name"] = v.get("name") or v.get("vendor_name")
        return v

    def create_vendor(self, data: dict):
        v_name = (data.get("vendor_name") or data.get("name", "")).strip()
        existing = self.vendor_repo.find_one({
            "$or": [{"name": v_name}, {"vendor_name": v_name}]
        })
        if existing:
            raise ValueError(f"Vendor '{v_name}' already exists")

        vendor_id = SequenceCounter.get_next_id("vendor")
        doc = {
            "_id": vendor_id,
            "organization_id": "ORG-001",
            "code": vendor_id,
            "name": v_name,
            "vendor_name": v_name,
            "contact": data.get("contact", ""),
            "email": data.get("email"),
            "address": data.get("address", ""),
            "country": data.get("country", "India"),
            "status": data.get("status", "ACTIVE")
        }
        self.vendor_repo.insert_one(doc)
        return doc

    def update_vendor(self, vendor_id: str, data: dict):
        v = self.get_vendor_by_id(vendor_id)
        update_data = {k: v for k, v in data.items() if k not in ["_id", "created_at"]}
        if "vendor_name" in update_data:
            update_data["name"] = update_data["vendor_name"]
        self.vendor_repo.update_one({"_id": v["_id"]}, {"$set": update_data})
        return self.get_vendor_by_id(v["_id"])

    # --- Parts ---
    def get_all_parts(self, search: str = None, part_type_id: str = None, vendor_id: str = None, tracking_type: str = None):
        query = {}
        if part_type_id:
            query["$or"] = [{"item_type_id": part_type_id}, {"part_type_id": part_type_id}]
        if vendor_id:
            query["vendor_id"] = vendor_id
        if tracking_type:
            query["$or"] = [{"tracking_mode": tracking_type}, {"tracking_type": tracking_type}]
        if search:
            query["$or"] = [
                {"code": {"$regex": search, "$options": "i"}},
                {"part_code": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}},
                {"part_name": {"$regex": search, "$options": "i"}},
                {"mpn": {"$regex": search, "$options": "i"}},
                {"mfr": {"$regex": search, "$options": "i"}}
            ]

        parts = self.part_repo.find_all(query, sort_by=[("code", 1)])
        for p in parts:
            p["part_code"] = p.get("code") or p.get("part_code")
            p["code"] = p.get("code") or p.get("part_code")
            p["part_name"] = p.get("name") or p.get("part_name")
            p["name"] = p.get("name") or p.get("part_name")
            p["part_id"] = p.get("_id")
            p["item_id"] = p.get("_id")
            p["part_type_id"] = p.get("item_type_id") or p.get("part_type_id")
            p["item_type_id"] = p.get("item_type_id") or p.get("part_type_id")
            p["tracking_type"] = p.get("tracking_mode") or p.get("tracking_type", "QUANTITY")
            p["tracking_mode"] = p.get("tracking_mode") or p.get("tracking_type", "QUANTITY")
            if p.get("vendor_id"):
                v = self.vendor_repo.find_by_id(p["vendor_id"])
                p["vendor_name"] = (v.get("name") or v.get("vendor_name")) if v else None
            if p.get("part_type_id"):
                pt = self.part_type_repo.find_by_id(p["part_type_id"])
                p["part_type_name"] = (pt.get("code") or pt.get("name") or pt.get("part_type_name")) if pt else None
        return parts

    def get_part_by_id(self, part_id: str):
        p = self.part_repo.find_by_id(part_id)
        if not p:
            p = self.part_repo.find_by_code(part_id)
        if not p:
            raise ValueError(f"Part {part_id} not found")
        p["part_code"] = p.get("code") or p.get("part_code")
        p["code"] = p.get("code") or p.get("part_code")
        p["part_name"] = p.get("name") or p.get("part_name")
        p["name"] = p.get("name") or p.get("part_name")
        p["part_id"] = p.get("_id")
        p["item_id"] = p.get("_id")
        p["part_type_id"] = p.get("item_type_id") or p.get("part_type_id")
        p["item_type_id"] = p.get("item_type_id") or p.get("part_type_id")
        p["tracking_type"] = p.get("tracking_mode") or p.get("tracking_type", "QUANTITY")
        p["tracking_mode"] = p.get("tracking_mode") or p.get("tracking_type", "QUANTITY")
        if p.get("vendor_id"):
            v = self.vendor_repo.find_by_id(p["vendor_id"])
            p["vendor_name"] = (v.get("name") or v.get("vendor_name")) if v else None
        if p.get("part_type_id"):
            pt = self.part_type_repo.find_by_id(p["part_type_id"])
            p["part_type_name"] = (pt.get("code") or pt.get("name") or pt.get("part_type_name")) if pt else None
            p["configured_fields"] = pt.get("fields") or self.field_repo.find_by_part_type(p["part_type_id"])
        return p

    def create_part(self, data: dict):
        part_code = (data.get("part_code") or data.get("code", "")).strip()
        if self.part_repo.find_by_code(part_code):
            raise ValueError(f"Part code '{part_code}' already exists")

        type_id = data.get("part_type_id") or data.get("item_type_id")
        pt = self.part_type_repo.find_by_id(type_id)
        if not pt:
            pt = self.part_type_repo.find_one({"code": str(type_id).strip().upper()})
        if not pt:
            raise ValueError(f"Part type '{type_id}' does not exist")

        type_id = pt["_id"]

        if data.get("vendor_id"):
            v = self.vendor_repo.find_by_id(data["vendor_id"])
            if not v:
                raise ValueError(f"Vendor '{data['vendor_id']}' does not exist")

        configured_fields = pt.get("fields") or self.field_repo.find_by_part_type(type_id) or []
        attributes = data.get("attributes", {}) or {}
        for f in configured_fields:
            f_key = f.get("field_key") or f.get("key") or (f.get("field_name") or f.get("name", "")).strip().lower().replace(" ", "_")
            f_name = f.get("field_name") or f.get("name") or f_key
            if f.get("required") and f_key and (f_key not in attributes or attributes[f_key] is None or str(attributes[f_key]).strip() == ""):
                raise ValueError(f"Attribute '{f_name}' ({f_key}) is required for part type '{pt.get('part_type_name') or pt.get('name') or pt.get('code')}'")

        part_id = SequenceCounter.get_next_id("part")
        part_name = (data.get("part_name") or data.get("name", "")).strip()
        tracking = data.get("tracking_type") or data.get("tracking_mode") or pt.get("tracking_mode", "QUANTITY")

        part_doc = {
            "_id": part_id,
            "organization_id": "ORG-001",
            "item_type_id": type_id,
            "part_type_id": type_id,
            "code": part_code,
            "part_code": part_code,
            "name": part_name,
            "part_name": part_name,
            "package": data.get("package", ""),
            "vendor_id": data.get("vendor_id"),
            "description": data.get("description", ""),
            "mfr": data.get("mfr", ""),
            "mpn": data.get("mpn", ""),
            "rohs": data.get("rohs", "YES"),
            "static_sensitive": data.get("static_sensitive", "NO"),
            "msl": data.get("msl", "NA"),
            "unit_of_measure": data.get("unit_of_measure", "PCS"),
            "tracking_mode": tracking,
            "tracking_type": tracking,
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
    def get_all_lots(self, part_id: str = None, org_id: str = "ORG-001"):
        from app.config.database import Database
        db = Database.get_db()
        if db is None:
            return []

        query = {"organization_id": org_id, "quantity": {"$gt": 0}}
        if part_id:
            matched_item = db.items.find_one({
                "organization_id": org_id,
                "$or": [{"_id": part_id}, {"code": part_id}, {"part_number": part_id}]
            })
            if matched_item:
                item_id_val = matched_item["_id"]
                item_code_val = matched_item.get("code")
                query["$or"] = [
                    {"item_id": item_id_val},
                    {"part_id": item_id_val},
                    {"item_id": item_code_val},
                    {"part_id": item_code_val},
                    {"item_code": item_code_val},
                    {"part_code": item_code_val}
                ]
            else:
                query["$or"] = [
                    {"item_id": part_id},
                    {"part_id": part_id},
                    {"item_code": part_id},
                    {"part_code": part_id}
                ]

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "lot_number": {"$ifNull": ["$lot_number", "STANDARD"]},
                        "item_id": "$item_id"
                    },
                    "total_quantity": {"$sum": "$quantity"},
                    "available_quantity": {"$sum": {"$ifNull": ["$available_quantity", "$quantity"]}},
                    "vendor_id": {"$first": "$vendor_id"},
                    "location_ids": {"$addToSet": "$location_id"},
                    "created_at": {"$min": "$created_at"}
                }
            },
            {"$sort": {"_id.lot_number": 1}}
        ]

        items_cache = {i["_id"]: i for i in db.items.find({"organization_id": org_id})}
        vendors_cache = {v["_id"]: v for v in db.vendors.find({"organization_id": org_id})}
        locations_cache = {l["_id"]: l for l in db.locations.find({"organization_id": org_id})}

        lots = []
        for agg in db.inventory.aggregate(pipeline):
            lot_num = agg["_id"]["lot_number"]
            item_id = agg["_id"]["item_id"]
            item = items_cache.get(item_id)
            vendor = vendors_cache.get(agg.get("vendor_id"))
            loc_ids = agg.get("location_ids", [])
            loc_codes = [
                locations_cache[lid].get("location_code") or locations_cache[lid].get("code") or lid
                for lid in loc_ids if lid in locations_cache
            ]
            primary_loc_code = loc_codes[0] if loc_codes else ""
            primary_loc_id = loc_ids[0] if loc_ids else None

            lots.append({
                "_id": lot_num,
                "lot_id": lot_num,
                "lot_batch_no": lot_num,
                "lot_number": lot_num,
                "part_id": item_id,
                "item_id": item_id,
                "part_code": item.get("code") if item else item_id,
                "item_code": item.get("code") if item else item_id,
                "part_name": item.get("name") if item else "",
                "item_name": item.get("name") if item else "",
                "vendor_id": agg.get("vendor_id"),
                "vendor_name": vendor.get("name") or vendor.get("vendor_name") if vendor else None,
                "location_id": primary_loc_id,
                "location_code": primary_loc_code,
                "location_ids": loc_ids,
                "locations": loc_codes,
                "quantity": agg.get("total_quantity", 0),
                "available_quantity": agg.get("available_quantity", agg.get("total_quantity", 0)),
                "received_date": agg.get("created_at", "")[:10] if agg.get("created_at") else "",
                "created_at": agg.get("created_at")
            })

        return lots

    def get_lot_by_id(self, lot_id: str, org_id: str = "ORG-001"):
        lots = self.get_all_lots(org_id=org_id)
        for l in lots:
            if l.get("lot_batch_no") == lot_id or l.get("_id") == lot_id or l.get("lot_number") == lot_id:
                return l
        raise ValueError(f"Lot '{lot_id}' not found")

    def create_lot(self, data: dict, session=None):
        batch_no = data["lot_batch_no"].strip()
        part_id = data.get("part_id") or data.get("item_id")
        return {
            "_id": batch_no,
            "part_id": part_id,
            "item_id": part_id,
            "lot_batch_no": batch_no,
            "lot_number": batch_no,
            "vendor_id": data.get("vendor_id"),
            "received_date": data.get("received_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }

    # --- Bulk Import & Templates ---
    def generate_import_template(self, file_format: str = "csv"):
        part_types = self.part_type_repo.find_all(sort_by=[("part_type_name", 1)])
        all_fields = self.field_repo.find_all({"active": True})

        # Discover unique dynamic field keys across all part types
        dynamic_cols = []
        seen_keys = set()
        for f in all_fields:
            key = f.get("field_key") or f.get("key") or (f.get("field_name") or f.get("name", "")).strip().lower().replace(" ", "_")
            if key and key not in seen_keys:
                seen_keys.add(key)
                dynamic_cols.append(f"attr_{key}")

        standard_headers = [
            "part_code", "part_name", "part_type", "tracking_type",
            "mpn", "mfr", "vendor", "package", "unit_of_measure",
            "rohs", "static_sensitive", "msl", "description"
        ]
        all_headers = standard_headers + dynamic_cols

        # Sample data rows
        sample_rows = [
            {
                "part_code": "RES-10K-0603",
                "part_name": "10K Ohm SMD Resistor 0603 1%",
                "part_type": "RESISTOR",
                "tracking_type": "QUANTITY",
                "mpn": "RC0603FR-0710KL",
                "mfr": "Yageo",
                "vendor": "DigiKey Electronics",
                "package": "0603",
                "unit_of_measure": "PCS",
                "rohs": "YES",
                "static_sensitive": "NO",
                "msl": "NA",
                "description": "Standard thick film chip resistor",
                "attr_resistance": "10k",
                "attr_tolerance": "1%",
                "attr_power_rating": "0.1W"
            },
            {
                "part_code": "CAP-100UF-16V",
                "part_name": "100uF 16V SMD Electrolytic Capacitor",
                "part_type": "CAPACITOR",
                "tracking_type": "QUANTITY",
                "mpn": "EEE-FK1C101P",
                "mfr": "Panasonic",
                "vendor": "Mouser Electronics",
                "package": "SMD",
                "unit_of_measure": "PCS",
                "rohs": "YES",
                "static_sensitive": "NO",
                "msl": "1",
                "description": "Aluminum electrolytic capacitor FK series",
                "attr_capacitance": "100uF",
                "attr_voltage": "16V"
            },
            {
                "part_code": "CELL-INR18650-35E",
                "part_name": "Samsung 3500mAh 18650 Li-ion Battery Cell",
                "part_type": "CELL",
                "tracking_type": "SERIAL",
                "mpn": "INR18650-35E",
                "mfr": "Samsung SDI",
                "vendor": "Molicel Global Supply",
                "package": "18650",
                "unit_of_measure": "PCS",
                "rohs": "YES",
                "static_sensitive": "NO",
                "msl": "NA",
                "description": "High capacity cylindrical lithium-ion cell",
                "attr_nominal_voltage": "3.6V",
                "attr_capacity": "3500mAh",
                "attr_chemistry": "NMC"
            }
        ]

        if file_format.lower() in ["xlsx", "excel"]:
            if not OPENPYXL_AVAILABLE:
                raise ValueError("Excel template generation requires 'openpyxl'. Please install openpyxl or download CSV format.")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Parts Catalog Template"


            # Header styling
            header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
            header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            align_center = Alignment(horizontal="center", vertical="center")

            # Write header
            ws.append(all_headers)
            for col_idx in range(1, len(all_headers) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center

            # Write sample data
            for item in sample_rows:
                row_vals = [item.get(h, "") for h in all_headers]
                ws.append(row_vals)

            # Auto column width
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "parts_import_template.xlsx"

        else: # CSV default
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=all_headers)
            writer.writeheader()
            for r in sample_rows:
                writer.writerow({h: r.get(h, "") for h in all_headers})
            return output.getvalue().encode("utf-8-sig"), "text/csv", "parts_import_template.csv"

    def bulk_import_parts(self, file_bytes: bytes, filename: str, duplicate_strategy: str = "skip"):
        """
        Parses and imports parts in bulk from CSV, Excel (.xlsx/.xls), or JSON.
        - Automatically creates vendors if they do not already exist.
        - Maps dynamic attributes according to part type configurations.
        - Handles duplicates per duplicate_strategy ('skip', 'update', 'error').
        """
        lower_name = (filename or "").lower()
        rows = []

        # 1. Parse File Content
        if lower_name.endswith(".json"):
            try:
                raw_json = json.loads(file_bytes.decode("utf-8"))
                rows = raw_json if isinstance(raw_json, list) else raw_json.get("parts", [])
            except Exception as e:
                raise ValueError(f"Invalid JSON file format: {str(e)}")
        elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
            if not OPENPYXL_AVAILABLE:
                raise ValueError("Excel file reading requires 'openpyxl'. Please install openpyxl or upload a CSV file.")
            try:
                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)

                ws = wb.active
                iter_rows = list(ws.iter_rows(values_only=True))
                if not iter_rows:
                    raise ValueError("The Excel worksheet is empty.")
                headers = [str(h).strip() if h is not None else "" for h in iter_rows[0]]
                for r in iter_rows[1:]:
                    if any(cell is not None and str(cell).strip() != "" for cell in r):
                        row_dict = {}
                        for idx, h in enumerate(headers):
                            if h:
                                row_dict[h] = r[idx] if idx < len(r) and r[idx] is not None else ""
                        rows.append(row_dict)
            except Exception as e:
                raise ValueError(f"Failed to read Excel file: {str(e)}")
        else: # Default CSV
            try:
                # Try utf-8-sig, utf-8, latin-1
                text = None
                for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
                    try:
                        text = file_bytes.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if text is None:
                    raise ValueError("Unable to decode CSV file with supported encodings (UTF-8, Latin-1).")

                reader = csv.DictReader(io.StringIO(text))
                for r in reader:
                    # Filter out purely blank rows
                    if any(val is not None and str(val).strip() != "" for val in r.values()):
                        # Clean keys and values
                        cleaned = {k.strip(): str(v).strip() if v is not None else "" for k, v in r.items() if k}
                        rows.append(cleaned)
            except Exception as e:
                raise ValueError(f"Failed to parse CSV file: {str(e)}")

        if not rows:
            raise ValueError("No data rows found to import in the uploaded file.")

        # 2. Pre-cache Part Types and Fields
        db_part_types = self.part_type_repo.find_all()
        part_types_by_id = {pt["_id"].upper(): pt for pt in db_part_types}
        part_types_by_name = {pt["part_type_name"].strip().upper(): pt for pt in db_part_types}

        fields_by_type_id = {}
        for pt in db_part_types:
            fields_by_type_id[pt["_id"]] = self.field_repo.find_by_part_type(pt["_id"])

        # 3. Pre-cache Vendors & Identify Missing Vendors to Auto-Create
        db_vendors = self.vendor_repo.find_all()
        vendors_by_id = {v["_id"].upper(): v for v in db_vendors}
        vendors_by_name = {v["vendor_name"].strip().upper(): v for v in db_vendors}

        # Collect unique vendor names specified in rows
        raw_vendors_in_file = set()
        for r in rows:
            v_val = (
                r.get("vendor") or r.get("vendor_name") or r.get("vendor_id") or
                r.get("Vendor") or r.get("Vendor Name") or ""
            )
            v_str = str(v_val).strip()
            if v_str:
                raw_vendors_in_file.add(v_str)

        # Auto-create non-existent vendors
        missing_vendor_names = []
        for v_name in raw_vendors_in_file:
            if v_name.upper() not in vendors_by_name and v_name.upper() not in vendors_by_id:
                missing_vendor_names.append(v_name)

        auto_created_vendors = []
        if missing_vendor_names:
            batch_vendor_ids = SequenceCounter.get_next_batch_ids("vendor", len(missing_vendor_names))
            now_iso = datetime.now(timezone.utc).isoformat()
            new_vendor_docs = []
            for v_id, v_name in zip(batch_vendor_ids, missing_vendor_names):
                v_doc = {
                    "_id": v_id,
                    "vendor_name": v_name,
                    "contact": "",
                    "email": None,
                    "address": "",
                    "country": "India",
                    "status": "ACTIVE",
                    "created_at": now_iso,
                    "updated_at": now_iso
                }
                new_vendor_docs.append(v_doc)
                vendors_by_name[v_name.upper()] = v_doc
                vendors_by_id[v_id.upper()] = v_doc
                auto_created_vendors.append(v_name)
            
            self.vendor_repo.insert_many(new_vendor_docs)

        # 4. Pre-check Existing Parts in Database
        raw_part_codes = []
        for r in rows:
            p_code = (r.get("part_code") or r.get("Part Code") or r.get("code") or r.get("part_no") or "")
            if p_code:
                raw_part_codes.append(str(p_code).strip())

        existing_parts_list = self.part_repo.find_all({"part_code": {"$in": raw_part_codes}})
        existing_parts_by_code = {p["part_code"].upper(): p for p in existing_parts_list}

        # 5. Process and Validate Each Row
        seen_codes_in_batch = set()
        errors = []
        to_insert_docs = []
        to_update_ops = []
        skipped_count = 0

        for row_idx, row in enumerate(rows, start=2): # 1-indexed header + 1
            # Standardize key lookup
            row_normalized = {k.strip().lower().replace(" ", "_"): v for k, v in row.items()}

            part_code = str(
                row_normalized.get("part_code") or row_normalized.get("code") or
                row_normalized.get("part_no") or ""
            ).strip()

            if not part_code:
                errors.append({"row": row_idx, "part_code": "N/A", "error": "Part code is required."})
                continue

            part_code_upper = part_code.upper()
            if part_code_upper in seen_codes_in_batch:
                errors.append({"row": row_idx, "part_code": part_code, "error": f"Duplicate part code '{part_code}' found multiple times within the import file."})
                continue
            seen_codes_in_batch.add(part_code_upper)

            part_name = str(
                row_normalized.get("part_name") or row_normalized.get("name") or
                row_normalized.get("description") or ""
            ).strip()
            if not part_name:
                errors.append({"row": row_idx, "part_code": part_code, "error": "Part name is required."})
                continue

            # Part Type resolution
            part_type_val = str(
                row_normalized.get("part_type") or row_normalized.get("type") or
                row_normalized.get("part_type_id") or row_normalized.get("part_type_name") or ""
            ).strip()

            target_pt = None
            if part_type_val:
                target_pt = part_types_by_id.get(part_type_val.upper()) or part_types_by_name.get(part_type_val.upper())
            elif len(db_part_types) == 1:
                target_pt = db_part_types[0]

            if not target_pt:
                errors.append({
                    "row": row_idx,
                    "part_code": part_code,
                    "error": f"Part type '{part_type_val}' not found. Available: {', '.join([pt['part_type_name'] for pt in db_part_types])}"
                })
                continue

            # Tracking Type
            tracking_type = str(
                row_normalized.get("tracking_type") or row_normalized.get("tracking") or ""
            ).strip().upper()
            if not tracking_type or tracking_type not in ["QUANTITY", "SERIAL"]:
                tracking_type = "SERIAL" if "CELL" in target_pt["part_type_name"] else "QUANTITY"

            # Vendor resolution
            vendor_val = str(
                row_normalized.get("vendor") or row_normalized.get("vendor_name") or
                row_normalized.get("vendor_id") or ""
            ).strip()
            matched_vendor = vendors_by_name.get(vendor_val.upper()) or vendors_by_id.get(vendor_val.upper()) if vendor_val else None
            vendor_id = matched_vendor["_id"] if matched_vendor else None

            # Dynamic Attributes resolution
            pt_fields = fields_by_type_id.get(target_pt["_id"], [])
            attributes = {}
            missing_required = []

            for field in pt_fields:
                f_key = field.get("field_key") or field.get("key") or (field.get("field_name") or field.get("name", "")).strip().lower().replace(" ", "_")
                f_name = (field.get("field_name") or field.get("name") or f_key).strip().lower().replace(" ", "_")
                display_name = field.get("field_name") or field.get("name") or f_key
                # Look for attr_key, key, attr_name, or name in row
                val = (
                    row_normalized.get(f"attr_{f_key}") or row_normalized.get(f_key) or
                    row_normalized.get(f"attr_{f_name}") or row_normalized.get(f_name)
                )

                if val is not None and str(val).strip() != "":
                    # Cast based on data_type
                    d_type = (field.get("data_type") or field.get("type") or "STRING").upper()
                    if d_type in ["NUMBER", "DECIMAL"]:
                        try:
                            num_val = float(val) if "." in str(val) else int(val)
                            attributes[f_key] = num_val
                        except (ValueError, TypeError):
                            attributes[f_key] = str(val).strip()
                    elif d_type == "BOOLEAN":
                        attributes[f_key] = str(val).strip().lower() in ["true", "yes", "1", "t", "y"]
                    else:
                        attributes[f_key] = str(val).strip()
                elif field.get("required"):
                    missing_required.append(f"{display_name} ({f_key})")

            # Collect any leftover attr_* columns
            for k, v in row_normalized.items():
                if k.startswith("attr_") and v is not None and str(v).strip() != "":
                    attr_name = k[5:]
                    if attr_name not in attributes:
                        attributes[attr_name] = str(v).strip()

            if missing_required:
                errors.append({
                    "row": row_idx,
                    "part_code": part_code,
                    "error": f"Missing required dynamic attributes for {target_pt['part_type_name']}: {', '.join(missing_required)}"
                })
                continue

            # Standard optional fields
            rohs_val = str(row_normalized.get("rohs") or "YES").strip().upper()
            rohs = rohs_val if rohs_val in ["YES", "NO", "NA"] else "YES"

            static_val = str(row_normalized.get("static_sensitive") or "NO").strip().upper()
            static_sensitive = static_val if static_val in ["YES", "NO"] else "NO"

            msl = str(row_normalized.get("msl") or "NA").strip()
            package = str(row_normalized.get("package") or "").strip()
            mpn = str(row_normalized.get("mpn") or "").strip()
            mfr = str(row_normalized.get("mfr") or row_normalized.get("manufacturer") or "").strip()
            unit_of_measure = str(row_normalized.get("unit_of_measure") or row_normalized.get("uom") or "PCS").strip()
            description = str(row_normalized.get("description") or "").strip()

            # Duplicate Check against database
            existing_part = existing_parts_by_code.get(part_code_upper)

            if existing_part:
                if duplicate_strategy == "skip":
                    skipped_count += 1
                    continue
                elif duplicate_strategy == "error":
                    errors.append({
                        "row": row_idx,
                        "part_code": part_code,
                        "error": f"Part code '{part_code}' already exists in the catalog."
                    })
                    continue
                elif duplicate_strategy == "update":
                    update_data = {
                        "part_name": part_name,
                        "package": package,
                        "vendor_id": vendor_id,
                        "description": description,
                        "mfr": mfr,
                        "mpn": mpn,
                        "rohs": rohs,
                        "static_sensitive": static_sensitive,
                        "msl": msl,
                        "unit_of_measure": unit_of_measure,
                        "attributes": attributes,
                        "active": True
                    }
                    to_update_ops.append(
                        UpdateOne({"_id": existing_part["_id"]}, {"$set": update_data})
                    )
            else:
                # Brand new part
                doc = {
                    "part_type_id": target_pt["_id"],
                    "part_code": part_code,
                    "part_name": part_name,
                    "package": package,
                    "vendor_id": vendor_id,
                    "description": description,
                    "mfr": mfr,
                    "mpn": mpn,
                    "rohs": rohs,
                    "static_sensitive": static_sensitive,
                    "msl": msl,
                    "unit_of_measure": unit_of_measure,
                    "tracking_type": tracking_type,
                    "attributes": attributes,
                    "active": True
                }
                to_insert_docs.append(doc)

        # 6. Allocate IDs and Commit to Database
        now_str = datetime.now(timezone.utc).isoformat()
        if to_insert_docs:
            batch_part_ids = SequenceCounter.get_next_batch_ids("part", len(to_insert_docs))
            for doc, p_id in zip(to_insert_docs, batch_part_ids):
                doc["_id"] = p_id
                doc["created_at"] = now_str
                doc["updated_at"] = now_str

        operations = []
        if to_insert_docs:
            operations.extend([InsertOne(d) for d in to_insert_docs])
        if to_update_ops:
            operations.extend(to_update_ops)

        if operations:
            self.part_repo.bulk_write(operations, ordered=False)

        return {
            "total_rows": len(rows),
            "imported": len(to_insert_docs),
            "updated": len(to_update_ops),
            "skipped": skipped_count,
            "auto_created_vendors": auto_created_vendors,
            "errors": errors
        }
