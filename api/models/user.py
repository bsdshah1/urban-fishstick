"""User model and schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    parent = "parent"
    teacher = "teacher"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    name: str
    role: UserRole = Field(default=UserRole.parent)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    id: int
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserCreate(SQLModel):
    email: str
    password: str
    name: str
    role: UserRole = UserRole.parent
