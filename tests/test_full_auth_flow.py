import secrets
import string
import pytest
import httpx

API_BASE = "http://localhost:8000"


def random_email() -> str:
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return f"user_{suffix}@example.com"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=API_BASE, timeout=10.0) as c:
        yield c


@pytest.fixture()
def user_credentials():
    return {"email": random_email(), "password": "Password123!"}


def test_full_auth_flow(client: httpx.Client, user_credentials):
    # Register
    r = client.post("/api/auth/register", json=user_credentials)
    assert r.status_code == 200, r.text
    reg = r.json()
    assert "access_token" in reg and "refresh_token" in reg
    access_token = reg["access_token"]
    refresh_token = reg["refresh_token"]

    # Login
    r = client.post("/api/auth/login", json=user_credentials)
    assert r.status_code == 200, r.text
    login = r.json()
    assert "access_token" in login and "refresh_token" in login
    access_token = login["access_token"]
    refresh_token = login["refresh_token"]

    # /me with access token
    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["email"] == user_credentials["email"]
    assert me["is_admin"] is False
    assert me["is_active"] is True

    # admin dashboard forbidden
    r = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {access_token}"})
    assert r.status_code == 403

    # Refresh token rotation
    r = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200, r.text
    refreshed = r.json()
    assert "access_token" in refreshed and "refresh_token" in refreshed
    new_access = refreshed["access_token"]
    new_refresh = refreshed["refresh_token"]
    assert new_refresh != refresh_token  # rotated

    # Logout with latest refresh token
    r = client.post("/api/auth/logout", json={"refresh_token": new_refresh})
    assert r.status_code == 200, r.text

    # Refresh again should fail (revoked)
    r = client.post("/api/auth/refresh", json={"refresh_token": new_refresh})
    assert r.status_code == 401

    # /me without token should be unauthorized
    r = client.get("/api/users/me")
    assert r.status_code == 401

