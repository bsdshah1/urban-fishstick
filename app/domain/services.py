"""Shared domain service contracts for feature modules.

Feature modules should depend on these protocols rather than reading curriculum
or policy files directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class CurriculumStep:
    year_group: str
    block: str
    objective: str
    small_step: str


@dataclass(frozen=True)
class ActivityTemplate:
    title: str
    cpa_stage: str
    description: str


@dataclass(frozen=True)
class TimesTableStatus:
    pupil_id: str
    mastered_tables: Sequence[int]
    focus_tables: Sequence[int]
    next_steps: Sequence[str]


@dataclass(frozen=True)
class CalculationMethod:
    year_group: str
    topic: str
    method_name: str
    steps: Sequence[str]


class CurriculumDomainService(Protocol):
    def get_curriculum_steps(
        self,
        *,
        year_group: str,
        block: str,
        objective: str,
    ) -> Sequence[CurriculumStep]: ...

    def get_times_table_expectations(self, *, year_group: str) -> Sequence[int]: ...


class LessonContentService(Protocol):
    def get_activity_templates(
        self,
        *,
        year_group: str,
        objective: str,
    ) -> Sequence[ActivityTemplate]: ...


class TimesTableProgressService(Protocol):
    def get_status(self, *, pupil_id: str) -> TimesTableStatus: ...

    def record_assessment(
        self,
        *,
        pupil_id: str,
        newly_mastered_tables: Sequence[int],
    ) -> TimesTableStatus: ...


class CalculationMethodService(Protocol):
    def get_method(self, *, year_group: str, topic: str) -> CalculationMethod: ...


class ParentCommunicationService(Protocol):
    def adapt_for_parent_audience(
        self,
        *,
        summary: str,
        reading_level: str,
        locale: str = "en-GB",
    ) -> str: ...
