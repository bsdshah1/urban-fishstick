"""Access control tests for times-table endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from api.auth import hash_password
from api.models.database import get_session
from api.models.pupil_guardianship import PupilGuardianship
from api.models.user import User, UserRole

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(TEST_ENGINE) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> TestClient:
    from interface.main import app

    app.dependency_overrides[get_session] = override_get_session

    SQLModel.metadata.create_all(TEST_ENGINE)
    with Session(TEST_ENGINE) as session:
        parent = User(
            email="parent-access@test.com",
            hashed_password=hash_password("testpass"),
            name="Parent User",
            role=UserRole.parent,
        )
        teacher = User(
            email="teacher-access@test.com",
            hashed_password=hash_password("testpass"),
            name="Teacher User",
            role=UserRole.teacher,
        )
        admin = User(
            email="admin-access@test.com",
            hashed_password=hash_password("testpass"),
            name="Admin User",
            role=UserRole.admin,
        )
        session.add(parent)
        session.add(teacher)
        session.add(admin)
        session.commit()

        session.add(PupilGuardianship(parent_user_id=parent.id, pupil_id="pupil-linked"))
        session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _token(client: TestClient, email: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "testpass"})
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.mark.parametrize(
    ("email", "pupil_id", "expected_status"),
    [
        ("parent-access@test.com", "pupil-linked", 200),
        ("parent-access@test.com", "pupil-unlinked", 403),
        ("teacher-access@test.com", "any-pupil", 200),
        ("admin-access@test.com", "any-pupil", 200),
    ],
)
def test_get_times_table_status_access(client: TestClient, email: str, pupil_id: str, expected_status: int):
    token = _token(client, email)

    res = client.get(
        f"/api/times-table/year-4/{pupil_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == expected_status


@pytest.mark.parametrize(
    ("email", "pupil_id", "expected_status"),
    [
        ("parent-access@test.com", "pupil-linked", 200),
        ("parent-access@test.com", "pupil-unlinked", 403),
        ("teacher-access@test.com", "any-pupil", 200),
        ("admin-access@test.com", "any-pupil", 200),
    ],
)
def test_record_assessment_access(client: TestClient, email: str, pupil_id: str, expected_status: int):
    token = _token(client, email)

    res = client.post(
        f"/api/times-table/year-4/{pupil_id}/assess",
        headers={"Authorization": f"Bearer {token}"},
        json={"newly_mastered_tables": [2, 3]},
    )

    assert res.status_code == expected_status


def test_denied_write_attempt_emits_audit_log_message(client: TestClient, caplog: pytest.LogCaptureFixture):
    token = _token(client, "parent-access@test.com")

    with caplog.at_level("WARNING"):
        res = client.post(
            "/api/times-table/year-4/pupil-unlinked/assess",
            headers={"Authorization": f"Bearer {token}"},
            json={"newly_mastered_tables": [6]},
        )

    assert res.status_code == 403
    assert "Denied times-table write attempt" in caplog.text
