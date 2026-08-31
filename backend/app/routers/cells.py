from flask import Blueprint, request, g
from app.schemas.validators import CellTransferSchema
from app.services.cell_service import CellService
from app.services.stock_service import StockService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

cells_bp = Blueprint("cells", __name__, url_prefix="/api/v1/cells")
cell_service = CellService()
stock_service = StockService()

@cells_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_cells():
    search = request.args.get("search")
    part_id = request.args.get("part_id")
    lot_id = request.args.get("lot_id")
    status = request.args.get("status")
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 50))
    try:
        result = cell_service.get_all_cells(search, part_id, lot_id, status=status, skip=skip, limit=limit)
        return success_response(result)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@cells_bp.route("/<string:cell_id>", methods=["GET"])
@jwt_required(optional=True)
def get_cell_by_id(cell_id):
    try:
        result = cell_service.get_cell_by_serial_or_id(cell_id)
        return success_response(result)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@cells_bp.route("/serial/<string:serial_no>", methods=["GET"])
@jwt_required(optional=True)
def get_cell_by_serial(serial_no):
    try:
        result = cell_service.get_cell_by_serial_or_id(serial_no)
        return success_response(result)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@cells_bp.route("/transfer", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def transfer_cell():
    schema = CellTransferSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.transfer_cell(data, user_id=user_id)
        return success_response(res, message="Cell transferred successfully")
    except Exception as e:
        return error_response("TRANSFER_FAILED", str(e), 400)
