import logging

import requests
from flask import current_app

from app.security.auth import decode_token, extract_role_from_payload
from app.services.keycloak_admin_service import KeycloakAdminService


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.keycloak_admin = KeycloakAdminService()

    def login(self, username_or_email: str, password: str):
        token_url = current_app.config.get("KEYCLOAK_TOKEN_URL") or (
            f"{current_app.config['KEYCLOAK_URL'].rstrip('/')}/realms/"
            f"{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/token"
        )
        payload = {
            "client_id": current_app.config.get("KEYCLOAK_CLIENT_ID", "mes-frontend"),
            "grant_type": "password",
            "username": username_or_email,
            "password": password,
            "scope": "openid profile email",
        }
        client_secret = current_app.config.get("KEYCLOAK_CLIENT_SECRET", "")
        if client_secret:
            payload["client_secret"] = client_secret

        try:
            response = requests.post(token_url, data=payload, timeout=10)
        except requests.RequestException as exc:
            raise ValueError(f"Keycloak authentication unavailable: {exc}") from exc
        if response.status_code != 200:
            try:
                message = response.json().get("error_description", "Invalid credentials")
            except ValueError:
                message = "Invalid credentials"
            raise ValueError(message)

        token_data = response.json()
        claims = decode_token(token_data["access_token"])
        username = claims.get("preferred_username") or claims.get("username") or username_or_email
        return {
            "token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
            "user": self._user_from_claims(claims, username),
        }

    def refresh_token(self, refresh_token_str: str):
        token_url = current_app.config.get("KEYCLOAK_TOKEN_URL") or (
            f"{current_app.config['KEYCLOAK_URL'].rstrip('/')}/realms/"
            f"{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/token"
        )
        payload = {
            "client_id": current_app.config.get("KEYCLOAK_CLIENT_ID", "mes-frontend"),
            "grant_type": "refresh_token",
            "refresh_token": refresh_token_str,
        }
        client_secret = current_app.config.get("KEYCLOAK_CLIENT_SECRET", "")
        if client_secret:
            payload["client_secret"] = client_secret
        try:
            response = requests.post(token_url, data=payload, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Token refresh failed ({response.status_code})")
            token_data = response.json()
            claims = decode_token(token_data["access_token"])
            username = claims.get("preferred_username") or claims.get("username", "user")
            return {
                "token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", refresh_token_str),
                "expires_in": token_data.get("expires_in"),
                "user": self._user_from_claims(claims, username),
            }
        except requests.RequestException as exc:
            raise ValueError(f"Failed to refresh session: {exc}") from exc

    def logout_keycloak(self, refresh_token_str: str):
        logout_url = current_app.config.get("KEYCLOAK_LOGOUT_URL") or (
            f"{current_app.config['KEYCLOAK_URL'].rstrip('/')}/realms/"
            f"{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/logout"
        )
        payload = {
            "client_id": current_app.config.get("KEYCLOAK_CLIENT_ID", "mes-frontend"),
            "refresh_token": refresh_token_str,
        }
        client_secret = current_app.config.get("KEYCLOAK_CLIENT_SECRET", "")
        if client_secret:
            payload["client_secret"] = client_secret
        try:
            requests.post(logout_url, data=payload, timeout=10)
        except requests.RequestException as exc:
            logger.warning("Keycloak logout request failed: %s", exc)
        return True

    def register(self, data: dict, created_by: str = "system"):
        return self.keycloak_admin.create_user(
            username=data["username"],
            email=data["email"],
            full_name=data.get("full_name", data["username"]),
            password=data["password"],
            role=data["role"],
        )

    def get_all_users(self, search=None, role=None, active=None):
        users = [
            self.keycloak_admin.get_user_representation(user["id"])
            for user in self.keycloak_admin.list_users(search)
        ]
        if role:
            users = [user for user in users if user["role"] == role.upper().strip()]
        if active is not None:
            users = [user for user in users if user["active"] == active]
        return sorted(users, key=lambda user: user.get("created_at") or "", reverse=True)

    def get_user_by_id(self, user_id):
        return self.keycloak_admin.get_user_representation(user_id)

    def update_user(self, user_id, data):
        return self.keycloak_admin.update_user(user_id, data)

    def reset_password(self, user_id, new_password):
        return self.keycloak_admin.reset_password(user_id, new_password)

    def enable_user(self, user_id):
        return self.keycloak_admin.enable_user(user_id)

    def disable_user(self, user_id):
        return self.keycloak_admin.disable_user(user_id)

    def delete_user(self, user_id):
        return self.keycloak_admin.delete_user(user_id)

    @staticmethod
    def _user_from_claims(claims, username):
        return {
            "_id": claims.get("sub", username),
            "username": username,
            "email": claims.get("email") or "",
            "full_name": claims.get("name") or claims.get("full_name") or username,
            "role": extract_role_from_payload(claims),
        }