from unittest.mock import patch

import jwt
from app.routers import auth as auth_router


def _token_for(app, role):
    with app.app_context():
        return jwt.encode(
            {"sub": f"{role.lower()}-id", "preferred_username": role.lower(), "role": role},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )


def test_register_requires_authentication(client):
    response = client.post("/api/v1/auth/register", json={})

    assert response.status_code == 401


def test_inventory_manager_can_register_user(app, client):
    token = _token_for(app, "INVENTORY_MANAGER")
    created_user = {
        "_id": "keycloak-user-id",
        "username": "new-user",
        "email": "new-user@example.com",
        "full_name": "New User",
        "role": "VIEWER",
        "active": True,
        "created_at": None,
    }

    with patch.object(auth_router.auth_service, "register", return_value=created_user):
        response = client.post(
            "/api/v1/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "new-user",
                "email": "new-user@example.com",
                "password": "Password@123",
                "full_name": "New User",
                "role": "VIEWER",
            },
        )

    assert response.status_code == 201
    assert response.json["data"]["_id"] == "keycloak-user-id"


def test_store_operator_cannot_register_user(app, client):
    token = _token_for(app, "STORE_OPERATOR")

    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 403