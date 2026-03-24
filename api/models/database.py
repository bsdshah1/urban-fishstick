"""Database engine and session management."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "beaumont.db"
DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
