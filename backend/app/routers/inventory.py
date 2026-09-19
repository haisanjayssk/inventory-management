from flask import Blueprint, request
from app.services.inventory_service import InventoryService
from app.repositories.cell_repository import CellInventoryRepository
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/v1")
inv_service = InventoryService()
cell_inv_repo = CellInventoryRepository()

@inventory_bp.route("/inventory", methods=["GET"])
@jwt_required(optional=True)
def get_inventory():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    search = request.args.get("search")
    item_type_id = request.args.get("item_type_id") or request.args.get("part_type_id")
    location_id = request.args.get("location_id")
    status = request.args.get("status")
    is_serialized_param = request.args.get("is_serialized")
    is_serialized = None
    if is_serialized_param is not None:
        is_serialized = is_serialized_param.lower() in ["true", "1", "yes"]
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    try:
        res = inv_service.get_all_inventory(
            org_id=org_id,
            search=search,
            item_type_id=item_type_id,
            location_id=location_id,
            status=status,
            is_serialized=is_serialized,
            skip=skip,
            limit=limit
        )
        return success_response(res)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/inventory/serial/<string:serial_no>", methods=["GET"])
@jwt_required(optional=True)
def get_inventory_by_serial(serial_no):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        data = inv_service.get_inventory_by_serial(serial_no, org_id)
        return success_response(data)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@inventory_bp.route("/inventory/part/<string:part_id>", methods=["GET"])
@inventory_bp.route("/inventory/item/<string:part_id>", methods=["GET"])
@jwt_required(optional=True)
def get_inventory_by_part(part_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        items = inv_service.get_inventory_by_part(part_id, org_id=org_id)
        return success_response(items)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/inventory/location/<string:location_id>", methods=["GET"])
@jwt_required(optional=True)
def get_inventory_by_location(location_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        res = inv_service.get_all_inventory(org_id=org_id, location_id=location_id, limit=200)
        return success_response(res.get("items", []))
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/cell-inventory/cell/<string:cell_id>", methods=["GET"])
@jwt_required(optional=True)
def get_cell_inventory(cell_id):
    try:
        item = cell_inv_repo.find_by_cell_id(cell_id)
        return success_response(item)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/cell-inventory/location/<string:location_id>", methods=["GET"])
@jwt_required(optional=True)
def get_cell_inventory_by_location(location_id):
    try:
        items = cell_inv_repo.find_by_location_id(location_id)
        return success_response(items)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)
