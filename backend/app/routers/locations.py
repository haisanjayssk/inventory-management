from flask import Blueprint, request
from app.schemas.validators import LocationSchema, BulkLocationGenerateSchema
from app.services.location_service import LocationService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

locations_bp = Blueprint("locations", __name__, url_prefix="/api/v1/locations")
location_service = LocationService()

@locations_bp.route("/warehouses", methods=["GET"])
@jwt_required(optional=True)
def get_warehouses():
    try:
        warehouses = location_service.get_warehouses()
        return success_response(warehouses)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@locations_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_locations():
    wh = request.args.get("warehouse_code")
    status = request.args.get("status")
    try:
        locs = location_service.get_all_locations(wh, status)
        return success_response(locs)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@locations_bp.route("/<string:loc_id>", methods=["GET"])
@jwt_required(optional=True)
def get_location(loc_id):
    try:
        loc = location_service.get_location_by_id(loc_id)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("/code/<string:location_code>", methods=["GET"])
@jwt_required(optional=True)
def get_location_by_code(location_code):
    try:
        loc = location_service.resolve_by_code(location_code)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("/nfc/<path:nfc_uid>", methods=["GET"])
@jwt_required(optional=True)
def get_location_by_nfc(nfc_uid):
    try:
        loc = location_service.resolve_by_nfc(nfc_uid)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_location():
    schema = LocationSchema()
    try:
        data = schema.load(request.get_json() or {})
        loc = location_service.create_location(data)
        return success_response(loc, message="Location created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@locations_bp.route("/bulk-generate", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def bulk_generate():
    schema = BulkLocationGenerateSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = location_service.bulk_generate_locations(data)
        return success_response(result, message=f"Generated {result['generated_count']} locations", status_code=201)
    except Exception as e:
        return error_response("BULK_GENERATE_FAILED", str(e), 400)

@locations_bp.route("/<string:loc_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_location(loc_id):
    try:
        data = request.get_json() or {}
        loc = location_service.update_location(loc_id, data)
        return success_response(loc, message="Location updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)
