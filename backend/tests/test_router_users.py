#/backend/tests/test_router_users.py
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db import get_db
from backend.tests.fakes.db import FakeConnection

# ----------------------------
# Test client (in-memory API)
# ----------------------------
client = TestClient(app)

# ----------------------------
# Dependency override
# ----------------------------
def override_get_db():
    yield FakeConnection(row=("testuser", "2025-01-01T00:00:00"))


app.dependency_overrides[get_db] = override_get_db


# ----------------------------
# Actual test
# ----------------------------
def test_register_user():
    response = client.post("/register/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword"
    })

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# ----------------------------
# Cleanup (important for test isolation)
# ----------------------------
#app.dependency_overrides = {}