from flask import Blueprint, request, g
from app.schemas.validators import ItemTypeSchema
from app.services.item_service import ItemService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

item_types_bp = Blueprint("item_types", __name__, url_prefix="/api/v1/item-types")
item_service = ItemService()

@item_types_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_item_types():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        types = item_service.get_all_item_types(org_id)
        return success_response(types)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@item_types_bp.route("/<string:item_type_id>", methods=["GET"])
@jwt_required(optional=True)
def get_item_type(item_type_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        item_type = item_service.get_item_type_by_id(item_type_id, org_id)
        return success_response(item_type)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@item_types_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_item_type():
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    schema = ItemTypeSchema()
    try:
        data = schema.load(request.get_json() or {})
        item_type = item_service.create_item_type(data, org_id)
        return success_response(item_type, message="Item type created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@item_types_bp.route("/<string:item_type_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_item_type(item_type_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        data = request.get_json() or {}
        item_type = item_service.update_item_type(item_type_id, data, org_id)
        return success_response(item_type, message="Item type updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)
