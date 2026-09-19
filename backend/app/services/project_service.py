from datetime import datetime, timezone
from app.repositories.project_repository import ProjectRepository
from app.models.counter import SequenceCounter

class ProjectService:
    def __init__(self):
        self.project_repo = ProjectRepository()

    def get_all_projects(self, org_id: str = "ORG-001"):
        return self.project_repo.find_all_by_org(org_id)

    def get_project_by_id(self, project_id: str, org_id: str = "ORG-001"):
        p = self.project_repo.find_one({"_id": project_id, "organization_id": org_id})
        if not p:
            p = self.project_repo.find_by_project_id(org_id, project_id)
        if not p:
            raise ValueError(f"Project '{project_id}' not found")
        return p

    def create_project(self, data: dict, org_id: str = "ORG-001"):
        code = data["project_id"].strip().upper()
        if self.project_repo.find_by_project_id(org_id, code):
            raise ValueError(f"Project ID '{code}' already exists")

        pid = SequenceCounter.get_next_id("project")
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "_id": pid,
            "organization_id": org_id,
            "project_id": code,
            "project_desc": data.get("project_desc", ""),
            "responsible_person": data.get("responsible_person", ""),
            "created_at": now,
            "updated_at": now
        }
        self.project_repo.insert_one(doc)
        return doc

    def update_project(self, project_id: str, data: dict, org_id: str = "ORG-001"):
        p = self.get_project_by_id(project_id, org_id)
        update_data = {k: v for k, v in data.items() if k not in ["_id", "organization_id", "created_at"]}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.project_repo.update_one({"_id": p["_id"]}, {"$set": update_data})
        return self.get_project_by_id(p["_id"], org_id)

    def delete_project(self, project_id: str, org_id: str = "ORG-001"):
        p = self.get_project_by_id(project_id, org_id)
        self.project_repo.delete_one({"_id": p["_id"]})
        return {"project_id": p["project_id"], "message": "Project deleted successfully"}
