import os
import pytest
from fastapi.testclient import TestClient

# Use a separate local DB url if you want; for quick demo this test just hits the app.
# For proper tests, point DATABASE_URL to a test DB and clear tables per run.
os.environ.setdefault("JWT_SECRET", "TEST_SECRET")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/secureauthx")

from app.main import create_app  # noqa: E402

@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)

def test_register_login_me(client: TestClient):
    email = "test@example.com"
    password = "password123"

    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 409)

    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and "refresh_token" in data

    access = data["access_token"]
    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == email
