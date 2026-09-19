from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.schemas.validators import UserRegisterSchema, UserUpdateSchema, UserPasswordResetSchema
from app.utils.responses import success_response, error_response

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")
auth_service = AuthService()

@users_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def get_users():
    search = request.args.get("search") or request.args.get("q")
    role = request.args.get("role")
    active_param = request.args.get("active")
    active = None
    if active_param is not None:
        active = active_param.lower() in ["true", "1", "yes"]

    try:
        users = auth_service.get_all_users(search=search, role=role, active=active)
        return success_response(users)
    except Exception as e:
        return error_response("FETCH_ERROR", str(e), 500)

@users_bp.route("/<string:user_id>", methods=["GET"])
@jwt_required(optional=True)
def get_user(user_id):
    try:
        user = auth_service.get_user_by_id(user_id)
        return success_response(user)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@users_bp.route("", methods=["POST"])
@jwt_required()
@require_roles("ADMIN")
def create_user():
    schema = UserRegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
        creator = g.current_user.get("username", "admin") if hasattr(g, "current_user") and g.current_user else "admin"
        result = auth_service.register(data, created_by=creator)
        return success_response(result, message="User created successfully", status_code=201)
    except Exception as e:
        return error_response("REGISTRATION_FAILED", str(e), 400)

@users_bp.route("/<string:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_roles("ADMIN")
def update_user(user_id):
    schema = UserUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
        user = auth_service.update_user(user_id, data)
        return success_response(user, message="User updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@users_bp.route("/<string:user_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN")
def delete_user(user_id):
    try:
        if hasattr(g, "current_user") and g.current_user and g.current_user.get("user_id") == user_id:
            return error_response("FORBIDDEN", "Cannot deactivate your own administrator account", 400)
        result = auth_service.delete_user(user_id)
        return success_response(result, message="User deactivated successfully")
    except Exception as e:
        return error_response("DELETE_FAILED", str(e), 400)
