def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@mes.com",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.json["data"]
    assert "token" in data
    assert data["user"]["role"] == "ADMIN"

def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin@mes.com",
        "password": "WrongPassword"
    })
    assert res.status_code == 401
    assert res.json["error"] == "INVALID_CREDENTIALS"

def test_me_endpoint(client, admin_token):
    res = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    assert res.json["data"]["username"] == "admin"

def test_keycloak_role_extraction():
    from app.security.auth import extract_role_from_payload

    # Direct role
    assert extract_role_from_payload({"role": "ADMIN"}) == "ADMIN"
    assert extract_role_from_payload({"role": "INVENTORY_MANAGER"}) == "INVENTORY_MANAGER"

    # Keycloak realm_access roles
    kc_payload_admin = {
        "preferred_username": "admin",
        "realm_access": {"roles": ["default-roles-mes-inventory", "offline_access", "ADMIN"]}
    }
    assert extract_role_from_payload(kc_payload_admin) == "ADMIN"

    kc_payload_manager = {
        "preferred_username": "manager",
        "realm_access": {"roles": ["INVENTORY_MANAGER", "offline_access"]}
    }
    assert extract_role_from_payload(kc_payload_manager) == "INVENTORY_MANAGER"

    kc_payload_operator = {
        "preferred_username": "operator",
        "realm_access": {"roles": ["STORE_OPERATOR"]}
    }
    assert extract_role_from_payload(kc_payload_operator) == "STORE_OPERATOR"

    kc_payload_viewer = {
        "preferred_username": "viewer",
        "realm_access": {"roles": ["VIEWER"]}
    }
    assert extract_role_from_payload(kc_payload_viewer) == "VIEWER"

    # Keycloak client resource_access roles
    kc_payload_client = {
        "resource_access": {
            "mes-frontend": {"roles": ["INVENTORY_MANAGER"]}
        }
    }
    assert extract_role_from_payload(kc_payload_client) == "INVENTORY_MANAGER"

    # Fallback to VIEWER
    assert extract_role_from_payload({}) == "VIEWER"

def test_refresh_missing_token(client):
    res = client.post("/api/v1/auth/refresh", json={})
    assert res.status_code == 400
    assert res.json["error"] == "MISSING_TOKEN"

def test_logout_endpoint(client):
    res = client.post("/api/v1/auth/logout", json={"refresh_token": "dummy-token"})
    assert res.status_code == 200
    assert res.json["message"] == "Logged out successfully"

