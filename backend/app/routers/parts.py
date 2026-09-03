import io
from flask import Blueprint, request, send_file
from app.schemas.validators import PartSchema
from app.services.part_service import PartService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

parts_bp = Blueprint("parts", __name__, url_prefix="/api/v1/parts")
part_service = PartService()

@parts_bp.route("/import-template", methods=["GET"])
def download_import_template():
    file_format = request.args.get("format", "csv").lower()
    try:
        content_bytes, mimetype, filename = part_service.generate_import_template(file_format)
        return send_file(
            io.BytesIO(content_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return error_response("TEMPLATE_ERROR", str(e), 500)

@parts_bp.route("/bulk-import", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def bulk_import():
    duplicate_strategy = request.form.get("duplicate_strategy") or request.args.get("duplicate_strategy", "skip")
    
    if "file" not in request.files:
        # Check if JSON payload was sent directly
        if request.is_json:
            try:
                import json
                file_bytes = json.dumps(request.get_json()).encode("utf-8")
                filename = "import.json"
                result = part_service.bulk_import_parts(file_bytes, filename, duplicate_strategy)
                return success_response(result, message="Bulk import processed successfully")
            except Exception as e:
                return error_response("BULK_IMPORT_FAILED", str(e), 400)
        return error_response("MISSING_FILE", "No file uploaded in 'file' field", 400)

    uploaded_file = request.files["file"]
    filename = uploaded_file.filename or "import.csv"
    file_bytes = uploaded_file.read()

    if not file_bytes:
        return error_response("EMPTY_FILE", "The uploaded file is empty", 400)

    try:
        result = part_service.bulk_import_parts(file_bytes, filename, duplicate_strategy)
        return success_response(result, message="Bulk import processed successfully")
    except Exception as e:
        return error_response("BULK_IMPORT_FAILED", str(e), 400)


@parts_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_parts():
    search = request.args.get("search")
    part_type_id = request.args.get("part_type_id")
    vendor_id = request.args.get("vendor_id")
    tracking_type = request.args.get("tracking_type")
    try:
        parts = part_service.get_all_parts(search, part_type_id, vendor_id, tracking_type)
        return success_response(parts)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@parts_bp.route("/<string:part_id>", methods=["GET"])
@jwt_required(optional=True)
def get_part(part_id):
    try:
        part = part_service.get_part_by_id(part_id)
        return success_response(part)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@parts_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_part():
    schema = PartSchema()
    try:
        data = schema.load(request.get_json() or {})
        part = part_service.create_part(data)
        return success_response(part, message="Part created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@parts_bp.route("/<string:part_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_part(part_id):
    try:
        data = request.get_json() or {}
        part = part_service.update_part(part_id, data)
        return success_response(part, message="Part updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@parts_bp.route("/<string:part_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN")
def delete_part(part_id):
    try:
        part_service.delete_part(part_id)
        return success_response(None, message="Part deactivated successfully")
    except Exception as e:
        return error_response("DELETE_FAILED", str(e), 400)
