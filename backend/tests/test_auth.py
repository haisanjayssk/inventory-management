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
