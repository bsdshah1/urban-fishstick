"""Parent-to-pupil ownership/link records."""

from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class PupilGuardianship(SQLModel, table=True):
    """Maps a parent user account to a pupil identifier they can access."""

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_user_id: int = Field(foreign_key="user.id", index=True)
    pupil_id: str = Field(index=True)
