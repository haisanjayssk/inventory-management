from app.repositories.base_repository import BaseRepository

class ProjectRepository(BaseRepository):
    def __init__(self):
        super().__init__("projects")

    def find_by_project_id(self, org_id: str, project_id: str, session=None):
        return self.find_one({
            "organization_id": org_id,
            "project_id": project_id.strip().upper()
        }, session=session)

    def find_all_by_org(self, org_id: str, session=None):
        return self.find_all({"organization_id": org_id}, sort_by=[("project_id", 1)], session=session)
