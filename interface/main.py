from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from app.features.lesson_planner.contracts import LessonPlannerResponse, LessonPhase
from app.domain.services import ActivityTemplate

app = FastAPI(title="Urban Fishstick Demo UI")


def build_demo_lesson_plan(year_group: str, block: str, objective: str) -> LessonPlannerResponse:
    phases = [
        LessonPhase(
            phase_name="Do Now",
            cpa_stage="concrete",
            activities=[
                ActivityTemplate(
                    title="Manipulatives warm-up",
                    cpa_stage="concrete",
                    description=f"Use counters to model {objective.lower()} in {block}.",
                )
            ],
        ),
        LessonPhase(
            phase_name="Teacher Model",
            cpa_stage="pictorial",
            activities=[
                ActivityTemplate(
                    title="Bar model walkthrough",
                    cpa_stage="pictorial",
                    description="Model one worked example with visual representations.",
                )
            ],
        ),
        LessonPhase(
            phase_name="Independent Practice",
            cpa_stage="abstract",
            activities=[
                ActivityTemplate(
                    title="Fluency + reasoning set",
                    cpa_stage="abstract",
                    description="Complete 6 fluency questions and 2 reasoning prompts.",
                )
            ],
        ),
    ]

    return LessonPlannerResponse(
        phases=phases,
        vocabulary_focus=["partition", "exchange", "efficient method"],
        references=[f"{year_group} / {block}", "CPA progression"],
    )


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Urban Fishstick Demo</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.4; }
      .card { border: 1px solid #ddd; border-radius: 10px; padding: 1rem; max-width: 900px; }
      code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }
      a.button { display:inline-block; background:#005bbb; color:white; text-decoration:none; padding:8px 12px; border-radius:6px; }
    </style>
  </head>
  <body>
    <h1>Urban Fishstick — Minimal Interface</h1>
    <div class=\"card\">
      <p>This is a starter UI for previewing one feature contract.</p>
      <p>Try the demo endpoint:</p>
      <p><a class=\"button\" href=\"/api/lesson-plan?year_group=Year%204&block=Multiplication%20and%20division&objective=Multiply%20a%202-digit%20number%20by%201-digit\">Generate demo lesson plan</a></p>
      <p>Or open interactive docs at <code>/docs</code>.</p>
    </div>
  </body>
</html>
"""


@app.get("/api/lesson-plan")
def lesson_plan(
    year_group: str = Query("Year 4"),
    block: str = Query("Multiplication and division"),
    objective: str = Query("Multiply a 2-digit number by 1-digit"),
) -> dict:
    response = build_demo_lesson_plan(year_group=year_group, block=block, objective=objective)
    return asdict(response)
