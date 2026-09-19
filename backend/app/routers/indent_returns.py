from flask import Blueprint, request, g
from app.schemas.validators import (
    IndentReturnCreateSchema,
    IndentReturnAcceptSchema
)
from app.services.indent_service import IndentService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

indent_returns_bp = Blueprint("indent_returns", __name__, url_prefix="/api/v1/indent-returns")
indent_service = IndentService()

@indent_returns_bp.route("", methods=["POST"])
@jwt_required()
def create_return():
    schema = IndentReturnCreateSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        ret = indent_service.create_return(data, g.current_user, org_id=org_id)
        return success_response(ret, message="Material return request submitted successfully", status_code=201)
    except Exception as e:
        return error_response("CREATE_RETURN_FAILED", str(e), 400)

@indent_returns_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_returns():
    try:
        org_id = g.current_user.get("organization_id", "ORG-001") if hasattr(g, "current_user") and g.current_user else "ORG-001"
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", request.args.get("limit", 50)))
        sort_by = request.args.get("sort_by", "created_at")
        sort_dir = -1 if request.args.get("sort_dir", "desc").lower() == "desc" else 1

        filters = {
            "status": request.args.get("status"),
            "indent_id": request.args.get("indent_id"),
            "requester_id": request.args.get("requester_id"),
            "q": request.args.get("q")
        }

        result = indent_service.get_all_returns(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
            org_id=org_id
        )
        return success_response(result)
    except Exception as e:
        return error_response("FETCH_RETURNS_FAILED", str(e), 500)

@indent_returns_bp.route("/<string:return_id>", methods=["GET"])
@jwt_required(optional=True)
def get_return(return_id):
    try:
        org_id = g.current_user.get("organization_id", "ORG-001") if hasattr(g, "current_user") and g.current_user else "ORG-001"
        ret = indent_service.get_return_by_id(return_id, org_id=org_id)
        return success_response(ret)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@indent_returns_bp.route("/<string:return_id>/accept", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def accept_return(return_id):
    schema = IndentReturnAcceptSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        result = indent_service.accept_return(return_id, data, g.current_user, org_id=org_id)
        return success_response(result, message="Material return processed and inspected successfully")
    except Exception as e:
        return error_response("ACCEPT_RETURN_FAILED", str(e), 400)
