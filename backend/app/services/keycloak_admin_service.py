import logging
from datetime import datetime, timezone

import requests
from flask import current_app


logger = logging.getLogger(__name__)

VALID_ROLES = ("ADMIN", "INVENTORY_MANAGER", "STORE_OPERATOR", "VIEWER")


class KeycloakAdminError(ValueError):
    pass


class KeycloakAdminPermissionError(PermissionError):
    pass


class KeycloakAdminService:
    def _base_url(self):
        return (
            f"{current_app.config['KEYCLOAK_URL'].rstrip('/')}/admin/realms/"
            f"{current_app.config['KEYCLOAK_REALM']}"
        )

    def _token(self):
        token_url = current_app.config.get("KEYCLOAK_TOKEN_URL") or (
            f"{current_app.config['KEYCLOAK_URL'].rstrip('/')}/realms/"
            f"{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/token"
        )
        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": current_app.config["KEYCLOAK_ADMIN_CLIENT_ID"],
                "client_secret": current_app.config["KEYCLOAK_ADMIN_CLIENT_SECRET"],
            },
            timeout=10,
        )
        if response.status_code != 200:
            raise KeycloakAdminError(
                f"Keycloak admin token request failed ({response.status_code}): "
                f"{self._response_message(response)}"
            )
        token = response.json().get("access_token")
        if not token:
            raise KeycloakAdminError("Keycloak admin token response had no access_token")
        return token

    @staticmethod
    def _response_message(response):
        try:
            body = response.json()
            return body.get("errorMessage") or body.get("error_description") or str(body)
        except ValueError:
            return response.text or "Unknown Keycloak error"

    def _request(self, method, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token()}"
        headers.setdefault("Content-Type", "application/json")
        response = requests.request(
            method,
            f"{self._base_url()}{path}",
            headers=headers,
            timeout=10,
            **kwargs,
        )
        if not 200 <= response.status_code < 300:
            if response.status_code in (401, 403):
                raise KeycloakAdminPermissionError(
                    f"Keycloak admin client is not authorized for {method} {path}: "
                    f"{self._response_message(response)}"
                )
            raise KeycloakAdminError(
                f"Keycloak admin request failed ({response.status_code}): "
                f"{self._response_message(response)}"
            )
        return response

    def list_users(self, search=None):
        params = {"max": 1000}
        if search:
            params["search"] = search
        return self._request("GET", "/users", params=params).json()

    def get_user(self, user_id):
        return self._request("GET", f"/users/{user_id}").json()

    def create_user(self, username, email, full_name, password, role, enabled=True):
        role = self._validate_role(role)
        first_name, separator, last_name = full_name.strip().partition(" ")
        if not separator:
            last_name = first_name
        response = self._request(
            "POST",
            "/users",
            json={
                "username": username.strip(),
                "email": email.strip().lower(),
                "firstName": first_name,
                "lastName": last_name,
                "enabled": enabled,
                "emailVerified": True,
                "attributes": {"full_name": [full_name.strip()]},
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }],
            },
        )
        location = response.headers.get("Location", "")
        user_id = location.rstrip("/").rsplit("/", 1)[-1] if location else None
        if not user_id:
            matches = self.list_users(username)
            user_id = next((user["id"] for user in matches if user.get("username") == username), None)
        if not user_id:
            raise KeycloakAdminError("Keycloak created the user but returned no user id")
        try:
            self.assign_role_to_user(user_id, role)
        except Exception:
            self.delete_user(user_id)
            raise
        return self.get_user_representation(user_id)

    def update_user(self, user_id, data):
        current = self.get_user(user_id)
        representation = {}
        if "full_name" in data and data["full_name"]:
            full_name = data["full_name"].strip()
            first_name, separator, last_name = full_name.partition(" ")
            representation["firstName"] = first_name
            representation["lastName"] = last_name if separator else first_name
            representation["attributes"] = {"full_name": [full_name]}
        if "email" in data and data["email"]:
            representation["email"] = data["email"].strip().lower()
        if "active" in data and data["active"] is not None:
            representation["enabled"] = bool(data["active"])
        if representation:
            self._request("PUT", f"/users/{user_id}", json={**current, **representation})
        if data.get("role"):
            self._replace_role(user_id, data["role"])
        return self.get_user_representation(user_id)

    def reset_password(self, user_id, password):
        self._request(
            "PUT",
            f"/users/{user_id}/reset-password",
            json={"type": "password", "value": password, "temporary": False},
        )
        return {"user_id": user_id, "message": "Password reset successfully"}

    def enable_user(self, user_id):
        return self.update_user(user_id, {"active": True})

    def disable_user(self, user_id):
        return self.update_user(user_id, {"active": False})

    def delete_user(self, user_id):
        self._request("DELETE", f"/users/{user_id}")
        return {"user_id": user_id, "message": "User deleted successfully"}

    def get_realm_roles(self):
        return self._request("GET", "/roles", params={"max": 1000}).json()

    def assign_role_to_user(self, user_id, role_name):
        role = self._get_allowed_role(role_name)
        self._request("POST", f"/users/{user_id}/role-mappings/realm", json=[role])

    def remove_role_from_user(self, user_id, role_name):
        role = self._get_allowed_role(role_name)
        self._request("DELETE", f"/users/{user_id}/role-mappings/realm", json=[role])

    def get_user_representation(self, user_id):
        user = self.get_user(user_id)
        roles = self._request("GET", f"/users/{user_id}/role-mappings/realm").json()
        role_names = {role.get("name") for role in roles}
        role = next((name for name in VALID_ROLES if name in role_names), "VIEWER")
        return self._to_frontend_user(user, role)

    def _replace_role(self, user_id, role_name):
        role_name = self._validate_role(role_name)
        current_roles = self._request("GET", f"/users/{user_id}/role-mappings/realm").json()
        removable = [role for role in current_roles if role.get("name") in VALID_ROLES]
        if removable:
            self._request("DELETE", f"/users/{user_id}/role-mappings/realm", json=removable)
        self.assign_role_to_user(user_id, role_name)

    def _get_allowed_role(self, role_name):
        role_name = self._validate_role(role_name)
        for user in self.list_users():
            roles = self._request(
                "GET", f"/users/{user['id']}/role-mappings/realm"
            ).json()
            for role in roles:
                if role.get("name") == role_name:
                    return {key: role[key] for key in ("id", "name") if key in role}
        raise KeycloakAdminError(f"Keycloak realm role {role_name} does not exist")

    @staticmethod
    def _validate_role(role_name):
        normalized = str(role_name or "").upper().strip()
        if normalized not in VALID_ROLES:
            raise KeycloakAdminError(f"Unsupported application role: {role_name}")
        return normalized

    @staticmethod
    def _to_frontend_user(user, role):
        attributes = user.get("attributes") or {}
        full_name = (attributes.get("full_name") or [None])[0]
        if not full_name:
            full_name = " ".join(filter(None, [user.get("firstName"), user.get("lastName")]))
        created_at = user.get("createdTimestamp")
        if created_at is not None:
            created_at = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc).isoformat()
        return {
            "_id": user["id"],
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "full_name": full_name or user.get("username", ""),
            "role": role,
            "active": bool(user.get("enabled", False)),
            "created_at": created_at,
        }