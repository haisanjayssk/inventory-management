from flask import Blueprint, request
from app.schemas.validators import VendorSchema
from app.services.part_service import PartService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

vendors_bp = Blueprint("vendors", __name__, url_prefix="/api/v1/vendors")
part_service = PartService()

@vendors_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_vendors():
    try:
        vendors = part_service.get_all_vendors()
        return success_response(vendors)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@vendors_bp.route("/<string:vendor_id>", methods=["GET"])
@jwt_required(optional=True)
def get_vendor(vendor_id):
    try:
        v = part_service.get_vendor_by_id(vendor_id)
        return success_response(v)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@vendors_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_vendor():
    schema = VendorSchema()
    try:
        data = schema.load(request.get_json() or {})
        v = part_service.create_vendor(data)
        return success_response(v, message="Vendor created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@vendors_bp.route("/<string:vendor_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_vendor(vendor_id):
    try:
        data = request.get_json() or {}
        v = part_service.update_vendor(vendor_id, data)
        return success_response(v, message="Vendor updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)
