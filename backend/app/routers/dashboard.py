from flask import Blueprint
from app.services.dashboard_service import DashboardService
from app.security.auth import jwt_required
from app.utils.responses import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")
dash_service = DashboardService()

@dashboard_bp.route("/metrics", methods=["GET"])
@jwt_required(optional=True)
def get_metrics():
    try:
        metrics = dash_service.get_metrics()
        return success_response(metrics)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)
