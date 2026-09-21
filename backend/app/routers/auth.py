from flask import Blueprint, request, g
from marshmallow import ValidationError
from app.schemas.validators import (
    UserLoginSchema, UserRegisterSchema, UserUpdateSchema, UserPasswordResetSchema
)
from app.services.auth_service import AuthService
from app.security.auth import jwt_required
from app.security.permissions import require_roles
from app.utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
auth_service = AuthService()

@auth_bp.route("/login", methods=["POST"])
def login():
    schema = UserLoginSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = auth_service.login(data["username_or_email"], data["password"])
        return success_response(result, message="Login successful")
    except Exception as e:
        return error_response("INVALID_CREDENTIALS", str(e), 401)

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return error_response("MISSING_TOKEN", "refresh_token is required", 400)
    try:
        result = auth_service.refresh_token(refresh_token)
        return success_response(result, message="Token refreshed successfully")
    except Exception as e:
        return error_response("REFRESH_FAILED", str(e), 401)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")
    if refresh_token:
        auth_service.logout_keycloak(refresh_token)
    return success_response(None, message="Logged out successfully")


@auth_bp.route("/register", methods=["POST"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def register():
    schema = UserRegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = auth_service.register(data, created_by=g.current_user["username"])
        return success_response(result, message="User registered successfully", status_code=201)
    except ValidationError as e:
        return error_response("REGISTRATION_FAILED", str(e), 400)
    except ValueError as e:
        return error_response("REGISTRATION_FAILED", str(e), 400)
    except PermissionError as e:
        return error_response("REGISTRATION_FORBIDDEN", str(e), 403)
    except Exception as e:
        return error_response("REGISTRATION_FAILED", str(e), 500)

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    return success_response(g.current_user)

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def get_users():
    search = request.args.get("search")
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

@auth_bp.route("/users/<string:user_id>", methods=["GET"])
@jwt_required()
@require_roles("ADMIN", "INVENTORY_MANAGER")
def get_user(user_id):
    try:
        user = auth_service.get_user_by_id(user_id)
        return success_response(user)
    except Exception as e:
        return error_response("NOT_FOUND", str(e), 404)

@auth_bp.route("/users/<string:user_id>", methods=["PUT"])
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

@auth_bp.route("/users/<string:user_id>/status", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN")
def set_user_status(user_id):
    data = request.get_json() or {}
    if not isinstance(data.get("active"), bool):
        return error_response("VALIDATION_ERROR", "active must be a boolean", 400)
    try:
        if data["active"]:
            user = auth_service.enable_user(user_id)
        else:
            user = auth_service.disable_user(user_id)
        return success_response(user, message="User status updated successfully")
    except Exception as e:
        return error_response("UPDATE_FAILED", str(e), 400)

@auth_bp.route("/users/<string:user_id>/password", methods=["PUT"])
@jwt_required()
@require_roles("ADMIN")
def reset_password(user_id):
    schema = UserPasswordResetSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = auth_service.reset_password(user_id, data["new_password"])
        return success_response(result, message="Password reset successfully")
    except Exception as e:
        return error_response("PASSWORD_RESET_FAILED", str(e), 400)

@auth_bp.route("/users/<string:user_id>", methods=["DELETE"])
@jwt_required()
@require_roles("ADMIN")
def delete_user(user_id):
    try:
        # Prevent admin from deleting own account
        if g.current_user.get("user_id") == user_id:
            return error_response("FORBIDDEN", "Cannot deactivate your own administrator account", 400)
        result = auth_service.delete_user(user_id)
        return success_response(result, message="User deleted successfully")
    except Exception as e:
        return error_response("DELETION_FAILED", str(e), 400)

