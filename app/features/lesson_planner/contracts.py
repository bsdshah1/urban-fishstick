"""API contracts for the lesson planner feature."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.services import ActivityTemplate, CurriculumDomainService, LessonContentService


@dataclass(frozen=True)
class LessonPlannerRequest:
    year_group: str
    block: str
    objective: str
    differentiation_profile: str


@dataclass(frozen=True)
class LessonPhase:
    phase_name: str
    cpa_stage: str
    activities: Sequence[ActivityTemplate]


@dataclass(frozen=True)
class LessonPlannerResponse:
    phases: Sequence[LessonPhase]
    vocabulary_focus: Sequence[str]
    references: Sequence[str]


@dataclass(frozen=True)
class LessonPlannerDependencies:
    curriculum_service: CurriculumDomainService
    lesson_content_service: LessonContentService
