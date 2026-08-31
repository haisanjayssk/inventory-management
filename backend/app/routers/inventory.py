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
    search = request.args.get("search")
    part_type_id = request.args.get("part_type_id")
    vendor_id = request.args.get("vendor_id")
    location_id = request.args.get("location_id")
    status = request.args.get("status")
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    try:
        res = inv_service.get_all_inventory(search, part_type_id, vendor_id, location_id, status, skip, limit)
        return success_response(res)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/inventory/part/<string:part_id>", methods=["GET"])
@jwt_required(optional=True)
def get_inventory_by_part(part_id):
    try:
        items = inv_service.inv_repo.find_by_part(part_id)
        return success_response(items)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@inventory_bp.route("/inventory/location/<string:location_id>", methods=["GET"])
@jwt_required(optional=True)
def get_inventory_by_location(location_id):
    try:
        items = inv_service.inv_repo.find_by_location(location_id)
        return success_response(items)
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
