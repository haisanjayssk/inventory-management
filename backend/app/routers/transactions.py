from flask import Blueprint, request
from app.services.transaction_service import TransactionService
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")
txn_service = TransactionService()

@transactions_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_transactions():
    txn_type = request.args.get("transaction_type")
    part_id = request.args.get("part_id")
    lot_id = request.args.get("lot_id")
    location_id = request.args.get("location_id")
    user_id = request.args.get("user_id")
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 50))
    try:
        res = txn_service.get_all_transactions(txn_type, part_id, lot_id, location_id, user_id, skip, limit)
        return success_response(res)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@transactions_bp.route("/<string:txn_id>", methods=["GET"])
@jwt_required(optional=True)
def get_transaction(txn_id):
    try:
        txn = txn_service.get_transaction_by_id(txn_id)
        return success_response(txn)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)
