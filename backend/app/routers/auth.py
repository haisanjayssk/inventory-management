from flask import Blueprint, request, g
from app.schemas.validators import UserLoginSchema, UserRegisterSchema
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
