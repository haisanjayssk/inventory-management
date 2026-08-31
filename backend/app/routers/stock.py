from flask import Blueprint, request, g
from app.schemas.validators import (
    StockReceiveSchema, StockIssueSchema, StockTransferSchema, StockReserveSchema, StockReleaseSchema
)
from app.services.stock_service import StockService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

stock_bp = Blueprint("stock", __name__, url_prefix="/api/v1/stock")
stock_service = StockService()

@stock_bp.route("/receive", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def receive_stock():
    schema = StockReceiveSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.receive(data, user_id=user_id)
        return success_response(res, message="Material received into stock successfully", status_code=201)
    except Exception as e:
        return error_response("RECEIVE_FAILED", str(e), 400)

@stock_bp.route("/issue", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def issue_stock():
    schema = StockIssueSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.issue(data, user_id=user_id)
        return success_response(res, message="Stock issued successfully")
    except Exception as e:
        return error_response("ISSUE_FAILED", str(e), 400)

@stock_bp.route("/transfer", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR")
def transfer_stock():
    schema = StockTransferSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.transfer(data, user_id=user_id)
        return success_response(res, message="Stock transferred successfully")
    except Exception as e:
        return error_response("TRANSFER_FAILED", str(e), 400)

@stock_bp.route("/reserve", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def reserve_stock():
    schema = StockReserveSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.reserve(data, user_id=user_id)
        return success_response(res, message="Stock reserved successfully")
    except Exception as e:
        return error_response("RESERVE_FAILED", str(e), 400)

@stock_bp.route("/release", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def release_stock():
    schema = StockReleaseSchema()
    try:
        data = schema.load(request.get_json() or {})
        user_id = g.current_user["user_id"] if hasattr(g, "current_user") and g.current_user else "system"
        res = stock_service.release(data, user_id=user_id)
        return success_response(res, message="Stock released successfully")
    except Exception as e:
        return error_response("RELEASE_FAILED", str(e), 400)
