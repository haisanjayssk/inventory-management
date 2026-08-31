from functools import wraps
from flask import g
from app.utils.responses import error_response

ROLE_HIERARCHY = {
    "ADMIN": 4,
    "INVENTORY_MANAGER": 3,
    "STORE_OPERATOR": 2,
    "VIEWER": 1
}

def require_roles(*allowed_roles):
    """
    Decorator to restrict endpoint access to specific roles.
    Example: @require_roles('ADMIN', 'INVENTORY_MANAGER')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                return error_response(
                    error_code="UNAUTHORIZED",
                    message="Authentication required",
                    status_code=401
                )

            user_role = current_user.get("role", "VIEWER")
            if user_role not in allowed_roles and "ADMIN" not in allowed_roles and user_role != "ADMIN":
                return error_response(
                    error_code="FORBIDDEN",
                    message=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                    status_code=403
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator
