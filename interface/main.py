"""Beaumont Maths Parent Companion — FastAPI application entry point.

Mounts all API routers and serves the React SPA from frontend/dist/.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.models.database import create_db_and_tables, engine
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


def _seed_database() -> None:
    """Seed users and import all generated digest JSON files if the DB is empty."""
    import json as _json
    from datetime import datetime
    from sqlmodel import Session, select
    from api.auth import hash_password
    from api.models.audit import AuditAction, AuditLog
    from api.models.digest import DigestStatus, WeeklyDigest
    from api.models.user import User, UserRole

    _GENERATED_DIR = Path(__file__).resolve().parent.parent / "app" / "content" / "generated" / "digests"

    with Session(engine) as session:
        # --- Users ---
        defaults = [
            ("teacher@beaumont.sch.uk", "Ms Clarke", UserRole.teacher),
            ("parent@beaumont.sch.uk", "Sample Parent", UserRole.parent),
            ("admin@beaumont.sch.uk", "School Admin", UserRole.admin),
        ]
        for email, name, role in defaults:
            if not session.exec(select(User).where(User.email == email)).first():
                session.add(User(
                    email=email,
                    hashed_password=hash_password("beaumont2024"),
                    name=name,
                    role=role,
                ))
        session.commit()

        teacher = session.exec(select(User).where(User.email == "teacher@beaumont.sch.uk")).first()

        # --- Digests (skip if already populated) ---
        if session.exec(select(WeeklyDigest)).first():
            return

        term_files: dict[tuple[str, str], list[Path]] = {}
        for json_file in sorted(_GENERATED_DIR.rglob("*.json")):
            try:
                data = _json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            key = (data.get("year_group", ""), data.get("term", ""))
            term_files.setdefault(key, []).append(json_file)

        for (year_group, term), files in sorted(term_files.items()):
            for week_num, json_file in enumerate(files, start=1):
                try:
                    data = _json.loads(json_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                content = data.get("content", {})
                dtq = content.get("dinner_table_questions", [])
                kv = content.get("key_vocabulary", [])
                eq = content.get("example_questions", [])
                now = datetime.utcnow()
                digest = WeeklyDigest(
                    year_group=year_group,
                    term=term,
                    week_number=week_num,
                    unit_title=data.get("unit_title") or data.get("block_name") or "Maths",
                    status=DigestStatus.published,
                    plain_english=content.get("plain_english", ""),
                    in_school=content.get("in_school", ""),
                    home_activity=content.get("home_activity", ""),
                    dinner_table_questions_json=_json.dumps(dtq if isinstance(dtq, list) else []),
                    key_vocabulary_json=_json.dumps(kv if isinstance(kv, list) else []),
                    example_questions_json=_json.dumps(eq if isinstance(eq, list) else []),
                    times_table_tip=content.get("times_table_tip", ""),
                    generated_by_ai=True,
                    approved_at=now,
                    published_at=now,
                    approved_by_id=teacher.id if teacher else None,
                )
                session.add(digest)
                session.flush()
                if teacher:
                    session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.published))
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    _warn_on_content_quality()
    create_db_and_tables()
    _seed_database()
    yield


app = FastAPI(
    title="Beaumont Maths Parent Companion",
    description="Weekly maths digests for Beaumont Primary School parents.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


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
