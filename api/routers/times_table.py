"""Times-table tracker API endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.auth import get_current_user
from api.models.database import get_session
from api.models.user import User
from api.services.pupil_access import PupilAccessService
from app.features.times_table_tracker.contracts import (
    TimesTableAssessmentEvent,
    TimesTableTrackerDependencies,
    TimesTableTrackerRequest,
)
from app.features.times_table_tracker.service import run_times_table_tracker
from services.adapters import CurriculumAdapter, InMemoryTimesTableProgressAdapter

router = APIRouter(prefix="/api/times-table", tags=["times_table"])

log = logging.getLogger(__name__)


def _assert_pupil_access(
    *,
    current_user: User,
    pupil_id: str,
    access_service: PupilAccessService,
    write_attempt: bool = False,
) -> None:
    if access_service.can_access_pupil(current_user=current_user, pupil_id=pupil_id):
        return

    if write_attempt:
        log.warning(
            "Denied times-table write attempt user_id=%s role=%s pupil_id=%s",
            current_user.id,
            current_user.role.value,
            pupil_id,
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this pupil record",
    )


def _get_access_service(session=Depends(get_session)) -> PupilAccessService:
    return PupilAccessService(session)

# Single shared adapter instance: in-memory state persists across requests
# within the same process (reset on server restart — suitable for demo).
_progress_adapter = InMemoryTimesTableProgressAdapter()


class TimesTableOut(BaseModel):
    pupil_id: str
    mastered_tables: list[int]
    focus_tables: list[int]
    next_steps: list[str]
    expectations_for_year: list[int]


class AssessmentIn(BaseModel):
    newly_mastered_tables: list[int]


def _run(year_group: str, pupil_id: str, event: TimesTableAssessmentEvent | None) -> TimesTableOut:
    req = TimesTableTrackerRequest(
        pupil_id=pupil_id,
        year_group=year_group,
        assessment_event=event,
    )
    deps = TimesTableTrackerDependencies(
        progress_service=_progress_adapter,
        curriculum_service=CurriculumAdapter(),
    )
    resp = run_times_table_tracker(req, deps)
    return TimesTableOut(
        pupil_id=pupil_id,
        mastered_tables=list(resp.mastered_tables),
        focus_tables=list(resp.focus_tables),
        next_steps=list(resp.next_steps),
        expectations_for_year=list(resp.expectations_for_year),
    )


@router.get("/{year_group}/{pupil_id}", response_model=TimesTableOut)
def get_times_table_status(
    year_group: str,
    pupil_id: str,
    current_user: User = Depends(get_current_user),
    access_service: PupilAccessService = Depends(_get_access_service),
) -> TimesTableOut:
    """Return the current times-table mastery status for a pupil."""
    _assert_pupil_access(current_user=current_user, pupil_id=pupil_id, access_service=access_service)
    return _run(year_group, pupil_id, event=None)


@router.post("/{year_group}/{pupil_id}/assess", response_model=TimesTableOut)
def record_assessment(
    year_group: str,
    pupil_id: str,
    body: AssessmentIn,
    current_user: User = Depends(get_current_user),
    access_service: PupilAccessService = Depends(_get_access_service),
) -> TimesTableOut:
    """Record newly mastered tables and return updated status."""
    _assert_pupil_access(
        current_user=current_user,
        pupil_id=pupil_id,
        access_service=access_service,
        write_attempt=True,
    )
    event = TimesTableAssessmentEvent(newly_mastered_tables=body.newly_mastered_tables)
    return _run(year_group, pupil_id, event=event)
