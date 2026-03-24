"""Helpers for validating user access to pupil records."""

from __future__ import annotations

from sqlmodel import Session, select

from api.models.pupil_guardianship import PupilGuardianship
from api.models.user import User, UserRole


class PupilAccessService:
    """Encapsulates role/ownership checks for pupil-level data."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def can_access_pupil(self, *, current_user: User, pupil_id: str) -> bool:
        if current_user.role in {UserRole.teacher, UserRole.admin}:
            return True
        if current_user.role != UserRole.parent:
            return False
        link = self._session.exec(
            select(PupilGuardianship).where(
                PupilGuardianship.parent_user_id == current_user.id,
                PupilGuardianship.pupil_id == pupil_id,
            )
        ).first()
        return link is not None
