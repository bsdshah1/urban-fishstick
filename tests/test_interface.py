"""Tests for the FastAPI application layer."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from api.auth import hash_password
from api.models.audit import AuditLog  # noqa: F401 — registers table metadata
from api.models.database import get_session
from api.models.digest import WeeklyDigest  # noqa: F401 — registers table metadata
from api.models.user import User, UserRole

# StaticPool keeps a single connection so in-memory tables persist across sessions
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(TEST_ENGINE) as session:
        yield session


@pytest.fixture(scope="module")
def client():
    # Import app after overriding the dependency
    from interface.main import app
    app.dependency_overrides[get_session] = override_get_session

    SQLModel.metadata.create_all(TEST_ENGINE)
    with Session(TEST_ENGINE) as session:
        session.add(User(
            email="teacher@test.com",
            hashed_password=hash_password("testpass"),
            name="Test Teacher",
            role=UserRole.teacher,
        ))
        session.add(User(
            email="parent@test.com",
            hashed_password=hash_password("testpass"),
            name="Test Parent",
            role=UserRole.parent,
        ))
        session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def teacher_token(client):
    res = client.post("/api/auth/login", json={"email": "teacher@test.com", "password": "testpass"})
    return res.json()["access_token"]


def test_login_returns_token(client):
    res = client.post("/api/auth/login", json={"email": "teacher@test.com", "password": "testpass"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "teacher"


def test_login_wrong_password_rejected(client):
    res = client.post("/api/auth/login", json={"email": "teacher@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_digests_requires_auth(client):
    res = client.get("/api/digests")
    assert res.status_code == 401


def test_teacher_can_list_all_digests(client, teacher_token):
    res = client.get("/api/digests", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_parent_only_sees_published_digests(client):
    login = client.post("/api/auth/login", json={"email": "parent@test.com", "password": "testpass"})
    token = login.json()["access_token"]
    res = client.get("/api/digests", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    for digest in res.json():
        assert digest["status"] == "published"


def test_dev_landing_html_contains_required_content():
    from interface.main import _dev_landing_html
    html = _dev_landing_html()
    assert "<!doctype html>" in html.lower()
    assert "Beaumont Maths" in html
    assert "/docs" in html
