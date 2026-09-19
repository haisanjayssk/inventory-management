from flask import Blueprint, request, g
from app.schemas.validators import (
    IndentCreateSchema,
    IndentUpdateSchema,
    IndentApprovalSchema,
    IndentRejectSchema,
    IndentIssueSchema
)
from app.services.indent_service import IndentService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

indents_bp = Blueprint("indents", __name__, url_prefix="/api/v1/indents")
indent_service = IndentService()

@indents_bp.route("", methods=["POST"])
@jwt_required()
def create_indent():
    schema = IndentCreateSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        indent = indent_service.create_indent(data, g.current_user, org_id=org_id)
        return success_response(indent, message="Indent created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATE_INDENT_FAILED", str(e), 400)

@indents_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_indents():
    try:
        org_id = g.current_user.get("organization_id", "ORG-001") if hasattr(g, "current_user") and g.current_user else "ORG-001"
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", request.args.get("limit", 50)))
        sort_by = request.args.get("sort_by", "created_at")
        sort_dir = -1 if request.args.get("sort_dir", "desc").lower() == "desc" else 1

        filters = {
            "status": request.args.get("status"),
            "project_id": request.args.get("project_id"),
            "requester_id": request.args.get("requester_id"),
            "project_head_id": request.args.get("project_head_id"),
            "priority": request.args.get("priority"),
            "site_id": request.args.get("site_id"),
            "q": request.args.get("q")
        }

        result = indent_service.get_all_indents(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
            org_id=org_id
        )
        return success_response(result)
    except Exception as e:
        return error_response("FETCH_INDENTS_FAILED", str(e), 500)

@indents_bp.route("/<string:indent_id>", methods=["GET"])
@jwt_required(optional=True)
def get_indent(indent_id):
    try:
        org_id = g.current_user.get("organization_id", "ORG-001") if hasattr(g, "current_user") and g.current_user else "ORG-001"
        indent = indent_service.get_indent_by_id(indent_id, org_id=org_id)
        return success_response(indent)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@indents_bp.route("/<string:indent_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_indent(indent_id):
    schema = IndentUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        updated = indent_service.update_indent(indent_id, data, g.current_user, org_id=org_id)
        return success_response(updated, message="Indent updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@indents_bp.route("/<string:indent_id>/submit", methods=["POST"])
@jwt_required()
def submit_indent(indent_id):
    try:
        org_id = g.current_user.get("organization_id", "ORG-001")
        submitted = indent_service.submit_indent(indent_id, g.current_user, org_id=org_id)
        return success_response(submitted, message="Indent submitted for approval")
    except Exception as e:
        return error_response("SUBMIT_FAILED", str(e), 400)

@indents_bp.route("/<string:indent_id>/approve", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "PROJECT_HEAD", "STORE_OPERATOR")
def approve_indent(indent_id):
    schema = IndentApprovalSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        approved = indent_service.approve_indent(indent_id, data, g.current_user, org_id=org_id)
        return success_response(approved, message="Indent approved successfully")
    except Exception as e:
        return error_response("APPROVAL_FAILED", str(e), 400)

@indents_bp.route("/<string:indent_id>/reject", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "PROJECT_HEAD", "STORE_OPERATOR")
def reject_indent(indent_id):
    schema = IndentRejectSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        rejected = indent_service.reject_indent(indent_id, data, g.current_user, org_id=org_id)
        return success_response(rejected, message="Indent rejected")
    except Exception as e:
        return error_response("REJECTION_FAILED", str(e), 400)

@indents_bp.route("/<string:indent_id>/issue", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def issue_stock(indent_id):
    schema = IndentIssueSchema()
    try:
        data = schema.load(request.get_json() or {})
        org_id = g.current_user.get("organization_id", "ORG-001")
        result = indent_service.issue_stock(indent_id, data, g.current_user, org_id=org_id)
        return success_response(result, message="Material issued successfully")
    except Exception as e:
        return error_response("ISSUE_FAILED", str(e), 400)

@indents_bp.route("/<string:indent_id>/close", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "PROJECT_HEAD", "STORE_OPERATOR")
def close_indent(indent_id):
    try:
        body = request.get_json() or {}
        notes = body.get("notes") or body.get("closure_notes")
        org_id = g.current_user.get("organization_id", "ORG-001")
        closed = indent_service.close_indent(indent_id, g.current_user, notes=notes, org_id=org_id)
        return success_response(closed, message="Indent closed successfully")
    except Exception as e:
        return error_response("CLOSE_FAILED", str(e), 400)
