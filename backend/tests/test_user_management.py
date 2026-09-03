import pytest

def test_list_users_as_admin(client, admin_token):
    res = client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    users = res.json["data"]
    assert len(users) >= 4
    # Check that passwords are NOT leaked
    for u in users:
        assert "password_hash" not in u
        assert "username" in u
        assert "role" in u

def test_create_and_manage_user_flow(client, admin_token, operator_token):
    # 1. Create a new user as Admin
    new_user_data = {
        "username": "test_engineer",
        "email": "engineer@mes.com",
        "password": "Password@123",
        "full_name": "Test Engineer",
        "role": "STORE_OPERATOR"
    }
    res_create = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_user_data
    )
    assert res_create.status_code == 201
    created_user = res_create.json["data"]
    user_id = created_user["_id"]
    assert created_user["username"] == "test_engineer"
    assert created_user["role"] == "STORE_OPERATOR"

    # 2. Verify login works with new credentials
    res_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "test_engineer",
        "password": "Password@123"
    })
    assert res_login.status_code == 200
    eng_token = res_login.json["data"]["token"]
    assert eng_token is not None

    # 3. Update user role to INVENTORY_MANAGER as Admin
    res_update = client.put(
        f"/api/v1/auth/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "INVENTORY_MANAGER", "full_name": "Lead Engineer"}
    )
    assert res_update.status_code == 200
    assert res_update.json["data"]["role"] == "INVENTORY_MANAGER"
    assert res_update.json["data"]["full_name"] == "Lead Engineer"

    # 4. Admin resets password
    res_reset = client.put(
        f"/api/v1/auth/users/{user_id}/password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "NewSecretPassword@999"}
    )
    assert res_reset.status_code == 200

    # 5. Old password fails
    res_old_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "test_engineer",
        "password": "Password@123"
    })
    assert res_old_login.status_code == 401

    # 6. New password succeeds
    res_new_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "engineer@mes.com",
        "password": "NewSecretPassword@999"
    })
    assert res_new_login.status_code == 200

    # 7. Deactivate user as Admin
    res_deactivate = client.delete(
        f"/api/v1/auth/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_deactivate.status_code == 200

    # 8. Deactivated user cannot log in
    res_deact_login = client.post("/api/v1/auth/login", json={
        "username_or_email": "test_engineer",
        "password": "NewSecretPassword@999"
    })
    assert res_deact_login.status_code == 401

def test_non_admin_cannot_create_or_delete_user(client, operator_token):
    # Store operator tries to register user -> Forbidden (403)
    res = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {operator_token}"},
        json={
            "username": "hacker_user",
            "email": "hacker@mes.com",
            "password": "Password@123",
            "full_name": "Hacker",
            "role": "ADMIN"
        }
    )
    assert res.status_code == 403
