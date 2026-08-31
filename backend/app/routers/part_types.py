from flask import Blueprint, request, g
from app.schemas.validators import PartTypeSchema, PartTypeFieldSchema
from app.services.part_service import PartService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

part_types_bp = Blueprint("part_types", __name__, url_prefix="/api/v1/part-types")
part_service = PartService()

@part_types_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_part_types():
    try:
        pts = part_service.get_all_part_types()
        return success_response(pts)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@part_types_bp.route("/<string:pt_id>", methods=["GET"])
@jwt_required(optional=True)
def get_part_type(pt_id):
    try:
        pt = part_service.get_part_type_by_id(pt_id)
        return success_response(pt)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@part_types_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_part_type():
    schema = PartTypeSchema()
    try:
        data = schema.load(request.get_json() or {})
        creator = g.current_user["username"] if hasattr(g, "current_user") and g.current_user else "admin"
        pt = part_service.create_part_type(data, created_by=creator)
        return success_response(pt, message="Part type created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@part_types_bp.route("/<string:pt_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_part_type(pt_id):
    try:
        data = request.get_json() or {}
        pt = part_service.update_part_type(pt_id, data)
        return success_response(pt, message="Part type updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@part_types_bp.route("/<string:pt_id>/fields", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def add_field(pt_id):
    schema = PartTypeFieldSchema()
    try:
        data = schema.load(request.get_json() or {})
        field_doc = part_service.add_field_to_part_type(pt_id, data)
        return success_response(field_doc, message="Field added successfully", status_code=201)
    except Exception as e:
        return error_response("FIELD_CREATION_FAILED", str(e), 400)

@part_types_bp.route("/fields/<string:field_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def delete_field(field_id):
    try:
        part_service.delete_field(field_id)
        return success_response(None, message="Field deleted successfully")
    except Exception as e:
        return error_response("DELETE_FAILED", str(e), 400)
