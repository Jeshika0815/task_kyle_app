import os
import sys

# Make `app` and `discord_ver` importable regardless of where pytest is invoked from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# auth_relation.py / calender_relation.py / database.py all read these at import
# time, so they must be set before anything under `app` is imported.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("ISSUER", "test-issuer")
os.environ.setdefault("AUDIENCE", "test-audience")
os.environ.setdefault("CLIENT_ID", "test-client-id")
os.environ.setdefault("CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("CLIENT_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
os.environ.setdefault("CLIENT_TOKEN_URI", "https://oauth2.googleapis.com/token")
os.environ.setdefault("ENDPOINT", "http://testserver")
os.environ.setdefault("MAP_API", "test-map-key")
os.environ.setdefault("DBUSER", "test")
os.environ.setdefault("ROOTPASS", "test")
os.environ.setdefault("DBHOST", "localhost")
os.environ.setdefault("DBPORT", "5432")
os.environ.setdefault("DATABASE", "test")
os.environ.setdefault("DISCORD_BOT_TOKEN", "test-discord-token")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# A single shared in-memory SQLite DB for the whole test session. StaticPool
# keeps one connection alive so every session sees the same data.
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _reset_db():
    """Give every test a clean set of tables."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register_user(client):
    """Register a user via the real /auth/register endpoint and return the response body."""

    def _register(email: str = "user@example.com", password: str = "password123"):
        payload = {
            "user": {
                "id": 0,
                "email": email,
                "password": password,
                "confirm_oauth": False,
            }
        }
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 200, res.text
        return res.json()

    return _register


@pytest.fixture
def auth_headers(client, register_user):
    """Register + log in a user, returning ready-to-use Authorization headers."""

    def _auth(email: str = "user@example.com", password: str = "password123"):
        register_user(email, password)
        res = client.post("/auth/login", data={"username": email, "password": password})
        assert res.status_code == 200, res.text
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth
