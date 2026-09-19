from datetime import datetime, timezone
from app.repositories.vendor_repository import VendorRepository
from app.models.counter import SequenceCounter

class VendorService:
    def __init__(self):
        self.vendor_repo = VendorRepository()

    def get_all_vendors(self, org_id: str = "ORG-001"):
        vendors = self.vendor_repo.find_all_by_org(org_id)
        for v in vendors:
            v["vendor_name"] = v.get("name") or v.get("vendor_name")
            if isinstance(v.get("contact"), dict):
                v["email"] = v.get("contact", {}).get("email") or v.get("email")
                v["phone"] = v.get("contact", {}).get("phone")
        return vendors

    def get_vendor_by_id(self, vendor_id: str, org_id: str = "ORG-001"):
        v = self.vendor_repo.find_one({"_id": vendor_id, "organization_id": org_id})
        if not v:
            v = self.vendor_repo.find_by_code(org_id, vendor_id)
        if not v:
            v = self.vendor_repo.find_by_name(org_id, vendor_id)
        if not v:
            raise ValueError(f"Vendor '{vendor_id}' not found")
        v["vendor_name"] = v.get("name") or v.get("vendor_name")
        return v

    def create_vendor(self, data: dict, org_id: str = "ORG-001"):
        name = (data.get("name") or data.get("vendor_name") or "").strip()
        if not name:
            raise ValueError("Vendor name is required")

        code = (data.get("code") or "").strip().upper()
        if not code:
            code = SequenceCounter.get_next_id("vendor")
        else:
            if self.vendor_repo.find_by_code(org_id, code):
                raise ValueError(f"Vendor code '{code}' already exists")

        vid = SequenceCounter.get_next_id("vendor")
        now = datetime.now(timezone.utc).isoformat()

        contact = data.get("contact", {})
        if isinstance(contact, str):
            contact = {"phone": contact, "email": data.get("email")}

        address = data.get("address", {})
        if isinstance(address, str):
            address = {"street": address, "country": data.get("country", "India")}

        doc = {
            "_id": vid,
            "organization_id": org_id,
            "code": code,
            "name": name,
            "vendor_name": name,
            "types": data.get("types", ["DISTRIBUTOR"]),
            "contact": contact,
            "address": address,
            "email": data.get("email") or (contact.get("email") if isinstance(contact, dict) else None),
            "site_id": data.get("site_id", "SITE-001"),
            "status": data.get("status", "ACTIVE"),
            "created_at": now,
            "updated_at": now
        }
        self.vendor_repo.insert_one(doc)
        return doc

    def update_vendor(self, vendor_id: str, data: dict, org_id: str = "ORG-001"):
        v = self.get_vendor_by_id(vendor_id, org_id)
        update_data = {k: v for k, v in data.items() if k not in ["_id", "organization_id", "created_at"]}
        if "name" in update_data:
            update_data["vendor_name"] = update_data["name"]
        elif "vendor_name" in update_data:
            update_data["name"] = update_data["vendor_name"]
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.vendor_repo.update_one({"_id": v["_id"]}, {"$set": update_data})
        return self.get_vendor_by_id(v["_id"], org_id)
