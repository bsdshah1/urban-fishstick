from __future__ import annotations

import json
from dataclasses import asdict
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from app.domain.services import ActivityTemplate
from app.features.lesson_planner.contracts import LessonPhase, LessonPlannerResponse

HOST = "127.0.0.1"
PORT = 8000


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


def render_home() -> str:
    return """<!doctype html>
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
      <p>This interface runs with Python standard library only (no external installs).</p>
      <p>Try the demo endpoint:</p>
      <p><a class=\"button\" href=\"/api/lesson-plan?year_group=Year%204&block=Multiplication%20and%20division&objective=Multiply%20a%202-digit%20number%20by%201-digit\">Generate demo lesson plan</a></p>
    </div>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/":
            body = render_home().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/api/lesson-plan":
            params = parse_qs(parsed.query)
            year_group = params.get("year_group", ["Year 4"])[0]
            block = params.get("block", ["Multiplication and division"])[0]
            objective = params.get("objective", ["Multiply a 2-digit number by 1-digit"])[0]

            payload = asdict(
                build_demo_lesson_plan(
                    year_group=year_group,
                    block=block,
                    objective=objective,
                )
            )
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
