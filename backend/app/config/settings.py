import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT = int(os.getenv("PORT", "5001"))
    HOST = os.getenv("HOST", "0.0.0.0")

    SECRET_KEY = os.getenv("SECRET_KEY", "mes-super-secret-production-inventory-key-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mes-jwt-secret-key-battery-electronic-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", "24")))

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "inventory_management_db")

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Keycloak Configuration
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080").rstrip("/")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "mes-inventory")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "mes-frontend")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    KEYCLOAK_ADMIN_CLIENT_ID = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID", "mes-backend")
    KEYCLOAK_ADMIN_CLIENT_SECRET = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", "")
    KEYCLOAK_ALGORITHM = os.getenv("KEYCLOAK_ALGORITHM", "RS256")

    KEYCLOAK_JWKS_URL = os.getenv("KEYCLOAK_JWKS_URL", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs")
    KEYCLOAK_TOKEN_URL = os.getenv("KEYCLOAK_TOKEN_URL", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token")
    KEYCLOAK_LOGOUT_URL = os.getenv("KEYCLOAK_LOGOUT_URL", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout")
    KEYCLOAK_USERINFO_URL = os.getenv("KEYCLOAK_USERINFO_URL", f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo")

