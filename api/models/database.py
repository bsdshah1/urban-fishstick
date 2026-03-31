"""Database engine and session management."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

# Priority:
#   1. DATABASE_URL env var (Vercel Postgres, Supabase, etc.)
#   2. /tmp/beaumont.db when running on Vercel (ephemeral — no persistence)
#   3. Local project-root SQLite for development
_env_url = os.environ.get("DATABASE_URL")
if _env_url:
    # Vercel Postgres uses "postgres://..." — SQLAlchemy needs "postgresql://..."
    DATABASE_URL = _env_url.replace("postgres://", "postgresql://", 1)
    _connect_args: dict = {}
elif os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/beaumont.db"
    _connect_args = {"check_same_thread": False}
else:
    _DB_PATH = Path(__file__).resolve().parent.parent.parent / "beaumont.db"
    DATABASE_URL = f"sqlite:///{_DB_PATH}"
    _connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
