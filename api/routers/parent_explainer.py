"""Parent explainer API endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.auth import get_current_user
from api.models.user import User
from app.features.parent_explainer.contracts import (
    ParentExplainerDependencies,
    ParentExplainerRequest,
)
from app.features.parent_explainer.service import run_parent_explainer
from services.adapters import CurriculumMethodAdapter, PlainEnglishCommunicationAdapter

router = APIRouter(prefix="/api/parent-explain", tags=["parent_explainer"])


class ParentExplainRequest(BaseModel):
    year_group: str
    topic: str
    reading_level: str = "plain"
    locale: str = "en-GB"


class ParentExplainOut(BaseModel):
    year_group: str
    topic: str
    summary: str
    method_steps: list[str]
    misconceptions: list[str]
    home_practice_tips: list[str]


@router.post("", response_model=ParentExplainOut)
def explain_for_parent(
    body: ParentExplainRequest,
    current_user: User = Depends(get_current_user),
) -> ParentExplainOut:
    """Generate a plain-English parent explainer for a maths topic."""
    req = ParentExplainerRequest(
        year_group=body.year_group,
        topic=body.topic,
        reading_level=body.reading_level,
        locale=body.locale,
    )
    deps = ParentExplainerDependencies(
        calculation_method_service=CurriculumMethodAdapter(),
        communication_service=PlainEnglishCommunicationAdapter(),
    )
    resp = run_parent_explainer(req, deps)

    return ParentExplainOut(
        year_group=body.year_group,
        topic=body.topic,
        summary=resp.summary,
        method_steps=list(resp.method_steps),
        misconceptions=list(resp.misconceptions),
        home_practice_tips=list(resp.home_practice_tips),
    )
