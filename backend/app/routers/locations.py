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
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        warehouses = location_service.get_warehouses(org_id=org_id)
        return success_response(warehouses)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@locations_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_locations():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    wh = request.args.get("warehouse_code")
    status = request.args.get("status")
    try:
        locs = location_service.get_all_locations(org_id=org_id, warehouse_code=wh, status=status)
        return success_response(locs)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@locations_bp.route("/<string:loc_id>", methods=["GET"])
@jwt_required(optional=True)
def get_location(loc_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        loc = location_service.get_location_by_id(loc_id, org_id=org_id)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("/code/<string:location_code>", methods=["GET"])
@jwt_required(optional=True)
def get_location_by_code(location_code):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        loc = location_service.resolve_by_code(location_code, org_id=org_id)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("/nfc/<path:nfc_uid>", methods=["GET"])
@jwt_required(optional=True)
def get_location_by_nfc(nfc_uid):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        loc = location_service.resolve_by_nfc(nfc_uid, org_id=org_id)
        return success_response(loc)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@locations_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_location():
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    schema = LocationSchema()
    try:
        data = schema.load(request.get_json() or {})
        loc = location_service.create_location(data, org_id=org_id)
        return success_response(loc, message="Location created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@locations_bp.route("/bulk-generate", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def bulk_generate():
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    schema = BulkLocationGenerateSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = location_service.bulk_generate_locations(data, org_id=org_id)
        return success_response(result, message=f"Generated {result['generated_count']} locations", status_code=201)
    except Exception as e:
        return error_response("BULK_GENERATE_FAILED", str(e), 400)

@locations_bp.route("/<string:loc_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_location(loc_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        data = request.get_json() or {}
        loc = location_service.update_location(loc_id, data, org_id=org_id)
        return success_response(loc, message="Location updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)
