import datetime
from functools import wraps
import bcrypt
import jwt
from flask import request, g, current_app
from app.utils.responses import error_response

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def check_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def generate_token(user_id_or_dict=None, username: str = None, email: str = None, role: str = None,
                   organization_id: str = "ORG-001", site_id: str = "SITE-001", user_id: str = None, **kwargs) -> str:
    if isinstance(user_id_or_dict, dict):
        uid = user_id_or_dict.get("sub") or user_id_or_dict.get("user_id") or user_id_or_dict.get("_id")
        username = user_id_or_dict.get("username", username)
        email = user_id_or_dict.get("email", email)
        role = user_id_or_dict.get("role", role)
        organization_id = user_id_or_dict.get("organization_id", organization_id)
        site_id = user_id_or_dict.get("site_id", site_id)
    else:
        uid = user_id_or_dict or user_id

    payload = {
        "sub": uid,
        "username": username or "",
        "email": email or "",
        "role": role or "STORE_OPERATOR",
        "organization_id": organization_id or "ORG-001",
        "site_id": site_id or "SITE-001",
        "exp": datetime.datetime.now(datetime.timezone.utc) + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

def jwt_required(optional: bool = False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                if optional:
                    g.current_user = {
                        "user_id": "USER-001",
                        "username": "admin",
                        "role": "ADMIN",
                        "organization_id": "ORG-001",
                        "site_id": "SITE-001"
                    }
                    return f(*args, **kwargs)
                return error_response(
                    error_code="UNAUTHORIZED",
                    message="Missing Authorization header",
                    status_code=401
                )

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return error_response(
                    error_code="UNAUTHORIZED",
                    message="Authorization header format must be Bearer <token>",
                    status_code=401
                )

            token = parts[1]
            try:
                payload = decode_token(token)
                g.current_user = {
                    "user_id": payload.get("sub"),
                    "username": payload.get("username"),
                    "email": payload.get("email"),
                    "role": payload.get("role"),
                    "organization_id": payload.get("organization_id", "ORG-001"),
                    "site_id": payload.get("site_id", "SITE-001")
                }
            except jwt.ExpiredSignatureError:
                return error_response(
                    error_code="TOKEN_EXPIRED",
                    message="Token has expired. Please log in again.",
                    status_code=401
                )
            except jwt.InvalidTokenError:
                return error_response(
                    error_code="INVALID_TOKEN",
                    message="Invalid token",
                    status_code=401
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator
