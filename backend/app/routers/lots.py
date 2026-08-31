from flask import Blueprint, request
from app.schemas.validators import LotSchema
from app.services.part_service import PartService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

lots_bp = Blueprint("lots", __name__, url_prefix="/api/v1/lots")
part_service = PartService()

@lots_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_lots():
    part_id = request.args.get("part_id")
    try:
        lots = part_service.get_all_lots(part_id)
        return success_response(lots)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@lots_bp.route("/<string:lot_id>", methods=["GET"])
@jwt_required(optional=True)
def get_lot(lot_id):
    try:
        lot = part_service.get_lot_by_id(lot_id)
        return success_response(lot)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@lots_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def create_lot():
    schema = LotSchema()
    try:
        data = schema.load(request.get_json() or {})
        lot = part_service.create_lot(data)
        return success_response(lot, message="Lot created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)
