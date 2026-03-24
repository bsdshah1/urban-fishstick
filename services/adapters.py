"""Concrete adapter implementations for domain service protocols.

Each class satisfies one protocol from app/domain/services.py using the
pre-built normalized curriculum data from services/curriculum_adapter.py.
"""

from __future__ import annotations

import re
from typing import ClassVar, Sequence

from app.domain.services import (
    ActivityTemplate,
    CalculationMethod,
    CurriculumStep,
    TimesTableStatus,
)
from services.curriculum_adapter import (
    get_method_stages,
    get_small_steps,
    get_times_table_expectation,
)

_CPA_STAGES = ("Concrete", "Pictorial", "Abstract")
_CPA_DESCRIPTIONS = (
    "Use physical objects and manipulatives to build understanding.",
    "Draw or use pictures and diagrams to represent the maths.",
    "Write the calculation using numbers and symbols.",
)


class CurriculumAdapter:
    """Implements CurriculumDomainService backed by normalized JSON datasets."""

    def get_curriculum_steps(
        self,
        *,
        year_group: str,
        block: str,
        objective: str,
    ) -> Sequence[CurriculumStep]:
        steps_text = get_small_steps(year_group, block)
        return [
            CurriculumStep(
                year_group=year_group,
                block=block,
                objective=objective,
                small_step=s,
            )
            for s in steps_text
        ]

    def get_times_table_expectations(self, *, year_group: str) -> Sequence[int]:
        exp = get_times_table_expectation(year_group)
        numbers = {int(n) for n in re.findall(r"\b\d+\b", exp) if 1 <= int(n) <= 12}
        return sorted(numbers)


class LessonContentAdapter:
    """Implements LessonContentService using CPA method stages."""

    def get_activity_templates(
        self,
        *,
        year_group: str,  # noqa: ARG002
        objective: str,
    ) -> Sequence[ActivityTemplate]:
        stages = get_method_stages(objective)
        # Ensure exactly 3 CPA stages
        while len(stages) < 3:
            stages = [*stages, _CPA_DESCRIPTIONS[len(stages)]]
        return [
            ActivityTemplate(
                title=f"{_CPA_STAGES[i]} activity",
                cpa_stage=_CPA_STAGES[i],
                description=stages[i],
            )
            for i in range(3)
        ]


class InMemoryTimesTableProgressAdapter:
    """Implements TimesTableProgressService with class-level in-memory state.

    Survives the request lifecycle but resets on process restart.
    Suitable for demo use; replace with a DB-backed adapter for production.
    """

    _store: ClassVar[dict[str, set[int]]] = {}

    def _build_status(self, pupil_id: str) -> TimesTableStatus:
        mastered = sorted(self._store.get(pupil_id, set()))
        focus = [t for t in range(2, 13) if t not in mastered][:3]
        next_steps = [
            f"Practise the {t} times table — try counting in {t}s." for t in focus
        ]
        return TimesTableStatus(
            pupil_id=pupil_id,
            mastered_tables=mastered,
            focus_tables=focus,
            next_steps=next_steps,
        )

    def get_status(self, *, pupil_id: str) -> TimesTableStatus:
        return self._build_status(pupil_id)

    def record_assessment(
        self,
        *,
        pupil_id: str,
        newly_mastered_tables: Sequence[int],
    ) -> TimesTableStatus:
        self._store.setdefault(pupil_id, set()).update(newly_mastered_tables)
        return self._build_status(pupil_id)


class CurriculumMethodAdapter:
    """Implements CalculationMethodService using CPA method stages."""

    def get_method(self, *, year_group: str, topic: str) -> CalculationMethod:
        stages = get_method_stages(topic)
        if not stages:
            stages = list(_CPA_DESCRIPTIONS)
        return CalculationMethod(
            year_group=year_group,
            topic=topic,
            method_name=f"{topic.title()} (CPA approach)",
            steps=stages,
        )


class PlainEnglishCommunicationAdapter:
    """Implements ParentCommunicationService.

    MVP passthrough: language level is already controlled by the AI generator
    and the structured content in the digest. A future version could apply
    readability transformations or translation here.
    """

    def adapt_for_parent_audience(
        self,
        *,
        summary: str,
        reading_level: str,  # noqa: ARG002
        locale: str = "en-GB",  # noqa: ARG002
    ) -> str:
        return summary
