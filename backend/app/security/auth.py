import datetime
from functools import wraps
import logging
import bcrypt
import jwt
from jwt import PyJWKClient
from flask import request, g, current_app
from app.utils.responses import error_response

logger = logging.getLogger(__name__)

# Cache JWKS clients by JWKS URL to prevent repeated instantiations
_jwks_clients = {}

VALID_ROLES_HIERARCHY = ["ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER"]

def get_jwks_client(jwks_url: str) -> PyJWKClient:
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
    return _jwks_clients[jwks_url]

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

def extract_role_from_payload(payload: dict) -> str:
    """
    Extracts the highest MES role from a JWT token payload.
    Supports direct 'role' claim, Keycloak 'realm_access.roles', and 'resource_access' client roles.
    """
    # 1. Direct role field
    direct_role = payload.get("role")
    if direct_role and str(direct_role).upper() in VALID_ROLES_HIERARCHY:
        return str(direct_role).upper()

    # 2. Keycloak realm_access roles
    realm_roles = payload.get("realm_access", {}).get("roles", [])
    for role_name in VALID_ROLES_HIERARCHY:
        if role_name in realm_roles:
            return role_name

    # 3. Keycloak resource_access client roles
    resource_access = payload.get("resource_access", {})
    for client_id, client_data in resource_access.items():
        client_roles = client_data.get("roles", [])
        for role_name in VALID_ROLES_HIERARCHY:
            if role_name in client_roles:
                return role_name

    return "VIEWER"

def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Supports Keycloak RS256 tokens via JWKS public keys, with fallback to HS256 for local/test tokens.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
    except Exception as e:
        raise jwt.InvalidTokenError(f"Malformed token header: {e}")

    if alg == "RS256":
        jwks_url = (
            current_app.config.get("KEYCLOAK_JWKS_URL")
            or f"{current_app.config.get('KEYCLOAK_URL', 'http://localhost:8080').rstrip('/')}/realms/{current_app.config.get('KEYCLOAK_REALM', 'mes-inventory')}/protocol/openid-connect/certs"
        )

        try:
            client = get_jwks_client(jwks_url)
            signing_key = client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
        except Exception as e:
            logger.error(f"Failed to verify Keycloak RS256 token via JWKS: {e}")
            raise jwt.InvalidTokenError(f"Keycloak token validation failed: {e}")
    elif alg == "HS256":
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"]
        )
    else:
        raise jwt.InvalidTokenError(f"Unsupported token algorithm: {alg}")

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
                role = extract_role_from_payload(payload)
                username = payload.get("preferred_username") or payload.get("username") or payload.get("sub", "user")
                email = payload.get("email") or f"{username}@mes.com"
                full_name = payload.get("name") or payload.get("full_name") or username

                g.current_user = {
                    "user_id": payload.get("sub"),
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "role": role
                }
            except jwt.ExpiredSignatureError:
                return error_response(
                    error_code="TOKEN_EXPIRED",
                    message="Token has expired. Please log in again.",
                    status_code=401
                )
            except jwt.InvalidTokenError as e:
                return error_response(
                    error_code="INVALID_TOKEN",
                    message=f"Invalid token: {str(e)}",
                    status_code=401
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator

