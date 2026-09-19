from flask import Blueprint, request
from app.services.transaction_service import TransactionService
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")
txn_service = TransactionService()

@transactions_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_transactions():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    txn_type = request.args.get("transaction_type")
    item_id = request.args.get("item_id") or request.args.get("part_id")
    location_id = request.args.get("location_id")
    user_id = request.args.get("user_id")
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    try:
        res = txn_service.get_all_transactions(
            org_id=org_id,
            txn_type=txn_type,
            item_id=item_id,
            location_id=location_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return success_response(res)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@transactions_bp.route("/<string:txn_id>", methods=["GET"])
@jwt_required(optional=True)
def get_transaction(txn_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        txn = txn_service.get_transaction_by_id(txn_id, org_id=org_id)
        return success_response(txn)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)
