from flask import Blueprint, request, g
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

@auth_bp.route("/register", methods=["POST"])
@jwt_required()
@require_roles("ADMIN")
def register():
    schema = UserRegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
        result = auth_service.register(data, created_by=g.current_user["username"])
        return success_response(result, message="User registered successfully", status_code=201)
    except Exception as e:
        return error_response("REGISTRATION_FAILED", str(e), 400)

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
        return success_response(result, message="User deactivated successfully")
    except Exception as e:
        return error_response("DELETION_FAILED", str(e), 400)

