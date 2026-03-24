"""Lesson planner API endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.auth import require_role
from api.models.user import User, UserRole
from app.features.lesson_planner.contracts import (
    LessonPlannerDependencies,
    LessonPlannerRequest,
)
from app.features.lesson_planner.service import run_lesson_planner
from services.adapters import CurriculumAdapter, LessonContentAdapter

router = APIRouter(prefix="/api/lesson-plan", tags=["lesson_planner"])


class LessonPlanRequest(BaseModel):
    year_group: str
    block: str
    objective: str
    differentiation_profile: str = "mixed"


class ActivityOut(BaseModel):
    title: str
    description: str


class LessonPhaseOut(BaseModel):
    phase_name: str
    cpa_stage: str
    activities: list[ActivityOut]


class LessonPlanOut(BaseModel):
    year_group: str
    block: str
    objective: str
    phases: list[LessonPhaseOut]
    vocabulary_focus: list[str]
    references: list[str]


@router.post("", response_model=LessonPlanOut, status_code=201)
def create_lesson_plan(
    body: LessonPlanRequest,
    current_user: User = Depends(require_role(UserRole.teacher, UserRole.admin)),
) -> LessonPlanOut:
    """Generate a CPA-structured lesson plan from curriculum data."""
    req = LessonPlannerRequest(
        year_group=body.year_group,
        block=body.block,
        objective=body.objective,
        differentiation_profile=body.differentiation_profile,
    )
    deps = LessonPlannerDependencies(
        curriculum_service=CurriculumAdapter(),
        lesson_content_service=LessonContentAdapter(),
    )
    resp = run_lesson_planner(req, deps)

    return LessonPlanOut(
        year_group=body.year_group,
        block=body.block,
        objective=body.objective,
        phases=[
            LessonPhaseOut(
                phase_name=p.phase_name,
                cpa_stage=p.cpa_stage,
                activities=[
                    ActivityOut(title=a.title, description=a.description)
                    for a in p.activities
                ],
            )
            for p in resp.phases
        ],
        vocabulary_focus=list(resp.vocabulary_focus),
        references=list(resp.references),
    )
