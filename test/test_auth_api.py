"""Tests for /auth/* — registration, login, and bot API keys."""


def test_register_creates_user(register_user):
    data = register_user(email="new@example.com", password="secret123")
    assert data["email"] == "new@example.com"


def test_register_duplicate_email_fails(client, register_user):
    register_user(email="dup@example.com", password="secret123")

    payload = {
        "user": {
            "id": 0,
            "email": "dup@example.com",
            "password": "some-other-password",
            "confirm_oauth": False,
        }
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 400


def test_login_success(client, register_user):
    register_user(email="login@example.com", password="mypassword")

    res = client.post("/auth/login", data={"username": "login@example.com", "password": "mypassword"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_fails(client, register_user):
    register_user(email="wrong@example.com", password="correct-password")

    res = client.post("/auth/login", data={"username": "wrong@example.com", "password": "incorrect"})
    assert res.status_code == 401


def test_login_unknown_user_fails(client):
    res = client.post("/auth/login", data={"username": "nobody@example.com", "password": "whatever"})
    assert res.status_code == 401


def test_protected_endpoint_requires_token(client):
    res = client.get("/task/")
    assert res.status_code in (401, 403)


def test_protected_endpoint_rejects_garbage_token(client):
    res = client.get("/task/", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_bot_token_can_authenticate_like_a_jwt(client, auth_headers):
    """/auth/bot_token issues a long-lived key that should work as a Bearer token too."""
    headers = auth_headers(email="bot@example.com", password="pw123456")

    res = client.post("/auth/bot_token", headers=headers)
    assert res.status_code == 200
    api_key = res.json()["api_key"]
    assert api_key

    res = client.get("/task/", headers={"Authorization": f"Bearer {api_key}"})
    assert res.status_code == 200


def test_bot_token_requires_authentication(client):
    res = client.post("/auth/bot_token")
    assert res.status_code in (401, 403)
