from flask import Blueprint
from app.services.report_service import ReportService
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")
report_service = ReportService()

@reports_bp.route("/stock-by-part", methods=["GET"])
@jwt_required(optional=True)
def stock_by_part():
    try:
        data = report_service.get_stock_by_part_report()
        return success_response(data)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@reports_bp.route("/location-occupancy", methods=["GET"])
@jwt_required(optional=True)
def location_occupancy():
    try:
        data = report_service.get_location_occupancy_report()
        return success_response(data)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)
