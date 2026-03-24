"""Admin endpoints: users and school settings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from api.auth import hash_password, require_role
from api.models.database import get_session
from api.models.user import User, UserCreate, UserRead, UserRole

router = APIRouter(prefix="/api/admin", tags=["admin"])

_SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "beaumont_settings.json"

_DEFAULT_SETTINGS = {
    "school_name": "Beaumont Primary School",
    "active_year_groups": ["year_2"],
    "current_term": "autumn",
    "current_week": 1,
}


def _load_settings() -> dict:
    if _SETTINGS_FILE.exists():
        return json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    return dict(_DEFAULT_SETTINGS)


def _save_settings(data: dict) -> None:
    _SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# --- Users ---

@router.get("/users", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_role(UserRole.admin)),
    session: Session = Depends(get_session),
) -> list[UserRead]:
    users = session.exec(select(User)).all()
    return [UserRead.model_validate(u) for u in users]


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(
    body: UserCreate,
    _: User = Depends(require_role(UserRole.admin)),
    session: Session = Depends(get_session),
) -> UserRead:
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
        role=body.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user)


@router.delete("/users/{user_id}", status_code=204)
def deactivate_user(
    user_id: int,
    _: User = Depends(require_role(UserRole.admin)),
    session: Session = Depends(get_session),
) -> None:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    session.add(user)
    session.commit()


# --- Settings ---

class SettingsRead(BaseModel):
    school_name: str
    active_year_groups: list[str]
    current_term: str
    current_week: int


class SettingsUpdate(BaseModel):
    current_term: Optional[str] = None
    current_week: Optional[int] = None
    active_year_groups: Optional[list[str]] = None


@router.get("/settings", response_model=SettingsRead)
def get_settings(_: User = Depends(require_role(UserRole.admin, UserRole.teacher))) -> SettingsRead:
    return SettingsRead(**_load_settings())


@router.patch("/settings", response_model=SettingsRead)
def update_settings(
    body: SettingsUpdate,
    _: User = Depends(require_role(UserRole.admin)),
) -> SettingsRead:
    settings = _load_settings()
    updates = body.model_dump(exclude_none=True)
    settings.update(updates)
    _save_settings(settings)
    return SettingsRead(**settings)
