"""Beaumont Maths Parent Companion — FastAPI application entry point.

Mounts all API routers and serves the React SPA from frontend/dist/.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.models.database import create_db_and_tables
from api.routers import admin, auth, digests, generate, lesson_planner, parent_explainer, times_table

_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
_QUALITY_REPORT = Path(__file__).resolve().parent.parent / "reports" / "content_quality" / "latest.json"

log = logging.getLogger(__name__)


def _dev_landing_html() -> str:
    """Return the dev-mode landing page HTML. Extracted for independent testability."""
    return """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Beaumont Maths — Dev</title></head>
<body style="font-family:sans-serif;padding:2rem">
  <h1>Beaumont Maths Parent Companion</h1>
  <p>Backend is running. Frontend not yet built.</p>
  <p>Run <code>cd frontend &amp;&amp; npm install &amp;&amp; npm run build</code> to build the UI.</p>
  <p>API docs: <a href="/docs">/docs</a></p>
</body>
</html>"""


def _warn_on_content_quality() -> None:
    """Log a warning for each unresolved content quality issue at startup."""
    if not _QUALITY_REPORT.exists():
        return
    report = json.loads(_QUALITY_REPORT.read_text(encoding="utf-8"))
    issues = [
        issue
        for result in report.get("results", [])
        for issue in result.get("issues", [])
    ]
    if not issues:
        return
    log.warning("Content quality: %d unresolved issue(s) in source markdown:", len(issues))
    for issue in issues:
        log.warning(
            "  [%s] %s line %s — %s",
            issue.get("check", "unknown"),
            issue.get("file", "?"),
            issue.get("line", "?"),
            issue.get("details", ""),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    _warn_on_content_quality()
    create_db_and_tables()
    yield


app = FastAPI(
    title="Beaumont Maths Parent Companion",
    description="Weekly maths digests for Beaumont Primary School parents.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- API routers ---
app.include_router(auth.router)
app.include_router(digests.router)
app.include_router(generate.router)
app.include_router(admin.router)
app.include_router(lesson_planner.router)
app.include_router(times_table.router)
app.include_router(parent_explainer.router)


# --- Static frontend (served after build) ---
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        """Serve the React SPA for all non-API routes."""
        index = _FRONTEND_DIST / "index.html"
        return FileResponse(str(index))
else:
    from fastapi.responses import HTMLResponse

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def dev_landing() -> str:
        return _dev_landing_html()
