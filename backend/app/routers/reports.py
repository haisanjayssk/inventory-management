from flask import Blueprint, request
from app.services.report_service import ReportService
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")
report_service = ReportService()

@reports_bp.route("/stock-by-part", methods=["GET"])
@reports_bp.route("/stock-by-item", methods=["GET"])
@jwt_required(optional=True)
def stock_by_part():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        data = report_service.get_stock_by_item_report(org_id=org_id)
        return success_response(data)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@reports_bp.route("/location-occupancy", methods=["GET"])
@jwt_required(optional=True)
def location_occupancy():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        data = report_service.get_location_occupancy_report(org_id=org_id)
        return success_response(data)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)
