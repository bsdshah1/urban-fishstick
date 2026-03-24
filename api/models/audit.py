"""AuditLog model."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class AuditAction(str, Enum):
    generated = "generated"
    edited = "edited"
    approved = "approved"
    published = "published"
    flagged = "flagged"
    republished = "republished"


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    digest_id: int = Field(foreign_key="weeklydigest.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    action: AuditAction
    note: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLogRead(SQLModel):
    id: int
    digest_id: int
    user_id: int
    action: AuditAction
    note: Optional[str]
    timestamp: datetime
