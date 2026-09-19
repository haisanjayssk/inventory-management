from datetime import datetime, timezone
from app.repositories.organization_repository import OrganizationRepository
from app.models.counter import SequenceCounter

class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()

    def get_all_organizations(self):
        return self.org_repo.find_all(sort_by=[("name", 1)])

    def get_organization_by_id(self, org_id: str):
        org = self.org_repo.find_one({"_id": org_id})
        if not org:
            org = self.org_repo.find_by_code(org_id)
        if not org:
            raise ValueError(f"Organization '{org_id}' not found")
        return org

    def create_organization(self, data: dict):
        code = data["code"].strip().upper()
        if self.org_repo.find_by_code(code):
            raise ValueError(f"Organization code '{code}' already exists")

        org_id = SequenceCounter.get_next_id("organization")
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "_id": org_id,
            "code": code,
            "name": data["name"].strip(),
            "country": data.get("country", "India"),
            "site": data.get("site", []),
            "status": data.get("status", "ACTIVE"),
            "created_at": now,
            "updated_at": now
        }
        self.org_repo.insert_one(doc)
        return doc

    def update_organization(self, org_id: str, data: dict):
        org = self.get_organization_by_id(org_id)
        update_data = {k: v for k, v in data.items() if k not in ["_id", "code", "created_at"]}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.org_repo.update_one({"_id": org["_id"]}, {"$set": update_data})
        return self.get_organization_by_id(org["_id"])
