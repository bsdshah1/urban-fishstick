"""Lesson planner orchestrator.

Receives a LessonPlannerRequest, calls domain service protocols,
and returns a LessonPlannerResponse.
"""

from __future__ import annotations

from app.features.lesson_planner.contracts import (
    LessonPhase,
    LessonPlannerDependencies,
    LessonPlannerRequest,
    LessonPlannerResponse,
)


def run_lesson_planner(
    req: LessonPlannerRequest,
    deps: LessonPlannerDependencies,
) -> LessonPlannerResponse:
    steps = deps.curriculum_service.get_curriculum_steps(
        year_group=req.year_group,
        block=req.block,
        objective=req.objective,
    )
    templates = deps.lesson_content_service.get_activity_templates(
        year_group=req.year_group,
        objective=req.objective,
    )

    phases = [
        LessonPhase(
            phase_name=f"{t.cpa_stage} Phase",
            cpa_stage=t.cpa_stage,
            activities=[t],
        )
        for t in templates
    ]

    vocabulary_focus = [s.small_step for s in steps[:5]]
    references = [
        "White Rose Maths Scheme of Learning",
        f"{req.year_group.replace('_', ' ').title()} — {req.block}",
    ]

    return LessonPlannerResponse(
        phases=phases,
        vocabulary_focus=vocabulary_focus,
        references=references,
    )
