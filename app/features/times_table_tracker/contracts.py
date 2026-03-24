"""API contracts for the times-table tracker feature."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.services import CurriculumDomainService, TimesTableProgressService


@dataclass(frozen=True)
class TimesTableAssessmentEvent:
    newly_mastered_tables: Sequence[int]


@dataclass(frozen=True)
class TimesTableTrackerRequest:
    pupil_id: str
    year_group: str
    assessment_event: TimesTableAssessmentEvent | None = None


@dataclass(frozen=True)
class TimesTableTrackerResponse:
    mastered_tables: Sequence[int]
    focus_tables: Sequence[int]
    next_steps: Sequence[str]
    expectations_for_year: Sequence[int]


@dataclass(frozen=True)
class TimesTableTrackerDependencies:
    progress_service: TimesTableProgressService
    curriculum_service: CurriculumDomainService
