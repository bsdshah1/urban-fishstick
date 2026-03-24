"""Times-table tracker orchestrator.

Receives a TimesTableTrackerRequest, calls domain service protocols,
and returns a TimesTableTrackerResponse.
"""

from __future__ import annotations

from app.features.times_table_tracker.contracts import (
    TimesTableTrackerDependencies,
    TimesTableTrackerRequest,
    TimesTableTrackerResponse,
)


def run_times_table_tracker(
    req: TimesTableTrackerRequest,
    deps: TimesTableTrackerDependencies,
) -> TimesTableTrackerResponse:
    expectations = deps.curriculum_service.get_times_table_expectations(
        year_group=req.year_group,
    )

    if req.assessment_event is not None:
        status = deps.progress_service.record_assessment(
            pupil_id=req.pupil_id,
            newly_mastered_tables=req.assessment_event.newly_mastered_tables,
        )
    else:
        status = deps.progress_service.get_status(pupil_id=req.pupil_id)

    focus_tables = [t for t in expectations if t not in status.mastered_tables][:3]

    return TimesTableTrackerResponse(
        mastered_tables=status.mastered_tables,
        focus_tables=focus_tables,
        next_steps=status.next_steps,
        expectations_for_year=list(expectations),
    )
