from flask import Blueprint, request
from app.schemas.validators import OrganizationSchema
from app.services.organization_service import OrganizationService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

organizations_bp = Blueprint("organizations", __name__, url_prefix="/api/v1/organizations")
org_service = OrganizationService()

@organizations_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_organizations():
    try:
        orgs = org_service.get_all_organizations()
        return success_response(orgs)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@organizations_bp.route("/<string:org_id>", methods=["GET"])
@jwt_required(optional=True)
def get_organization(org_id):
    try:
        org = org_service.get_organization_by_id(org_id)
        return success_response(org)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@organizations_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN")
def create_organization():
    schema = OrganizationSchema()
    try:
        data = schema.load(request.get_json() or {})
        org = org_service.create_organization(data)
        return success_response(org, message="Organization created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@organizations_bp.route("/<string:org_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN")
def update_organization(org_id):
    try:
        data = request.get_json() or {}
        org = org_service.update_organization(org_id, data)
        return success_response(org, message="Organization updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)
