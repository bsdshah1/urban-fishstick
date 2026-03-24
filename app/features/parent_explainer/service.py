"""Parent explainer orchestrator.

Receives a ParentExplainerRequest, calls domain service protocols,
and returns a ParentExplainerResponse.
"""

from __future__ import annotations

from app.features.parent_explainer.contracts import (
    ParentExplainerDependencies,
    ParentExplainerRequest,
    ParentExplainerResponse,
)


def run_parent_explainer(
    req: ParentExplainerRequest,
    deps: ParentExplainerDependencies,
) -> ParentExplainerResponse:
    method = deps.calculation_method_service.get_method(
        year_group=req.year_group,
        topic=req.topic,
    )

    year_label = req.year_group.replace("_", " ").title()
    raw_summary = (
        f"In {year_label}, children are learning {req.topic} "
        f"using the {method.method_name}. "
        f"They move from using physical objects, to pictures, to written numbers — "
        f"always building understanding before speed."
    )

    summary = deps.communication_service.adapt_for_parent_audience(
        summary=raw_summary,
        reading_level=req.reading_level,
        locale=req.locale,
    )

    misconceptions = [
        "Children often rush to written calculations before they fully understand why they work. "
        "Starting with physical objects builds real confidence.",
        "The school method may look different from how you learned it — "
        "stick with it at home to avoid confusion.",
    ]

    home_practice_tips = [
        f"Ask your child to explain {req.topic} to you. If they can teach it, they truly understand it.",
        "Use everyday objects (coins, pasta, grapes) to make the maths concrete before using pencil and paper.",
        "Little and often works best: five minutes of practice daily beats thirty minutes once a week.",
    ]

    return ParentExplainerResponse(
        summary=summary,
        method_steps=list(method.steps),
        misconceptions=misconceptions,
        home_practice_tips=home_practice_tips,
    )
