import pytest
from app.main import create_app
from app.config.settings import Config
from app.config.database import Database

class TestConfig(Config):
    TESTING = True
    DEBUG = False
    MONGO_DB_NAME = "inventory_management_test_db"

@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    yield app
    # Cleanup test DB after tests
    client = Database.get_client()
    if client:
        client.drop_database(TestConfig.MONGO_DB_NAME)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    return res.json["data"]["token"]

@pytest.fixture
def operator_token(client):
    res = client.post("/api/v1/auth/login", json={
        "username_or_email": "operator",
        "password": "Operator@123"
    })
    assert res.status_code == 200
    return res.json["data"]["token"]

@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

