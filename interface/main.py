"""Beaumont Maths Parent Companion — FastAPI application entry point.

Mounts all API routers and serves the React SPA from frontend/dist/.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.models.database import create_db_and_tables
from api.routers import auth, digests, generate, admin

_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
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


