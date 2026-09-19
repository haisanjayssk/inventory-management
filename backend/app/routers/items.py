import io
from flask import Blueprint, request, send_file
from app.schemas.validators import ItemSchema
from app.services.item_service import ItemService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

items_bp = Blueprint("items", __name__, url_prefix="/api/v1/items")
item_service = ItemService()

@items_bp.route("/import-template", methods=["GET"])
def download_import_template():
    file_format = request.args.get("format", "csv").lower()
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        content_bytes, mimetype, filename = item_service.generate_import_template(org_id, file_format)
        return send_file(
            io.BytesIO(content_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return error_response("TEMPLATE_ERROR", str(e), 500)

@items_bp.route("/bulk-import", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def bulk_import():
    duplicate_strategy = request.form.get("duplicate_strategy") or request.args.get("duplicate_strategy", "skip")
    org_id = getattr(request, "organization_id", None) or "ORG-001"

    if "file" not in request.files:
        if request.is_json:
            try:
                import json
                file_bytes = json.dumps(request.get_json()).encode("utf-8")
                filename = "import.json"
                result = item_service.bulk_import_items(file_bytes, filename, org_id, duplicate_strategy)
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
        result = item_service.bulk_import_items(file_bytes, filename, org_id, duplicate_strategy)
        return success_response(result, message="Bulk import processed successfully")
    except Exception as e:
        return error_response("BULK_IMPORT_FAILED", str(e), 400)

@items_bp.route("/export", methods=["GET"])
@jwt_required(optional=True)
def export_items():
    file_format = request.args.get("format", "csv").lower()
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        content_bytes, mimetype, filename = item_service.export_items(org_id, file_format)
        return send_file(
            io.BytesIO(content_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return error_response("EXPORT_ERROR", str(e), 500)

@items_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_items():
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    search = request.args.get("search")
    item_type_id = request.args.get("item_type_id") or request.args.get("part_type_id")
    active_only = request.args.get("active_only", "false").lower() == "true"
    try:
        items = item_service.get_all_items(org_id, item_type_id, search, active_only)
        return success_response(items)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@items_bp.route("/<string:item_id>", methods=["GET"])
@jwt_required(optional=True)
def get_item(item_id):
    org_id = getattr(request, "organization_id", None) or request.args.get("organization_id", "ORG-001")
    try:
        item = item_service.get_item_by_id(item_id, org_id)
        return success_response(item)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@items_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def create_item():
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    schema = ItemSchema()
    try:
        data = schema.load(request.get_json() or {})
        item = item_service.create_item(data, org_id)
        return success_response(item, message="Item created successfully", status_code=201)
    except Exception as e:
        return error_response("CREATION_FAILED", str(e), 400)

@items_bp.route("/<string:item_id>", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def update_item(item_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        data = request.get_json() or {}
        item = item_service.update_item(item_id, data, org_id)
        return success_response(item, message="Item updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@items_bp.route("/<string:item_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN")
def delete_item(item_id):
    org_id = getattr(request, "organization_id", None) or "ORG-001"
    try:
        res = item_service.delete_item(item_id, org_id)
        return success_response(res, message="Item deactivated successfully")
    except Exception as e:
        return error_response("DELETE_FAILED", str(e), 400)
