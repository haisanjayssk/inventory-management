from datetime import datetime, timezone
from flask import jsonify, request

def success_response(data=None, message="Operation successful", status_code=200, meta=None):
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code

def error_response(error_code="BAD_REQUEST", message="An error occurred", status_code=400, details=None):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status_code,
        "error": error_code,
        "message": message,
        "path": request.path if request else None
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status_code
