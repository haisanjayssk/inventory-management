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

def generate_token(user_id: str, username: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "email": email,
        "role": role,
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
                    g.current_user = None
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
                    "role": payload.get("role")
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
