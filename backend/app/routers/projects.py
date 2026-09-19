from flask import Blueprint, request
from app.schemas.validators import ProjectSchema
from app.services.project_service import ProjectService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

projects_bp = Blueprint("projects", __name__, url_prefix="/api/v1/projects")
project_service = ProjectService()

@projects_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_projects():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        projects = project_service.get_all_projects(org_id)
        return success_response(projects)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@projects_bp.route("/<string:project_id>", methods=["GET"])
@jwt_required(optional=True)
def get_project(project_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        project = project_service.get_project_by_id(project_id, org_id)
        return success_response(project)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@projects_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_project():
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    schema = ProjectSchema()
    try:
        data = schema.load(request.get_json() or {})
        project = project_service.create_project(data, org_id)
        return success_response(project, message="Project created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@projects_bp.route("/<string:project_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_project(project_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        data = request.get_json() or {}
        project = project_service.update_project(project_id, data, org_id)
        return success_response(project, message="Project updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@projects_bp.route("/<string:project_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN")
def delete_project(project_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        res = project_service.delete_project(project_id, org_id)
        return success_response(res, message="Project deleted successfully")
    except Exception as e:
        return error_response("DELETE_FAILED", str(e), 400)
