"""WeeklyDigest model and schemas."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlmodel import Field, SQLModel


class DigestStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    published = "published"
    flagged = "flagged"


class WeeklyDigest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year_group: str = Field(index=True)
    term: str  # "autumn" | "spring" | "summer"
    week_number: int
    unit_title: str
    status: DigestStatus = Field(default=DigestStatus.draft)

    # Content sections (stored as plain text; JSON fields stored as JSON strings)
    plain_english: str = Field(default="")
    in_school: str = Field(default="")
    home_activity: str = Field(default="")
    dinner_table_questions_json: str = Field(default="[]")  # JSON list[str]
    key_vocabulary_json: str = Field(default="[]")  # JSON list[{term, definition}]
    example_questions_json: str = Field(default="[]")  # JSON list[str]
    times_table_tip: str = Field(default="")
    teacher_note: Optional[str] = Field(default=None)

    generated_by_ai: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    @property
    def dinner_table_questions(self) -> list[str]:
        return json.loads(self.dinner_table_questions_json)

    @property
    def key_vocabulary(self) -> list[dict[str, str]]:
        return json.loads(self.key_vocabulary_json)

    @property
    def example_questions(self) -> list[str]:
        return json.loads(self.example_questions_json)


class DigestRead(SQLModel):
    id: int
    year_group: str
    term: str
    week_number: int
    unit_title: str
    status: DigestStatus
    plain_english: str
    in_school: str
    home_activity: str
    dinner_table_questions: list[str]
    key_vocabulary: list[dict[str, Any]]
    example_questions: list[str]
    times_table_tip: str
    teacher_note: Optional[str]
    generated_by_ai: bool
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    published_at: Optional[datetime]
    approved_by_id: Optional[int]

    @classmethod
    def from_orm(cls, digest: WeeklyDigest) -> "DigestRead":
        return cls(
            id=digest.id,
            year_group=digest.year_group,
            term=digest.term,
            week_number=digest.week_number,
            unit_title=digest.unit_title,
            status=digest.status,
            plain_english=digest.plain_english,
            in_school=digest.in_school,
            home_activity=digest.home_activity,
            dinner_table_questions=digest.dinner_table_questions,
            key_vocabulary=digest.key_vocabulary,
            example_questions=digest.example_questions,
            times_table_tip=digest.times_table_tip,
            teacher_note=digest.teacher_note,
            generated_by_ai=digest.generated_by_ai,
            created_at=digest.created_at,
            updated_at=digest.updated_at,
            approved_at=digest.approved_at,
            published_at=digest.published_at,
            approved_by_id=digest.approved_by_id,
        )


class DigestCreate(SQLModel):
    year_group: str
    term: str
    week_number: int
    unit_title: str
    plain_english: str = ""
    in_school: str = ""
    home_activity: str = ""
    dinner_table_questions: list[str] = Field(default_factory=list)
    key_vocabulary: list[dict[str, Any]] = Field(default_factory=list)
    example_questions: list[str] = Field(default_factory=list)
    times_table_tip: str = ""
    teacher_note: Optional[str] = None
    generated_by_ai: bool = False


class DigestUpdate(SQLModel):
    plain_english: Optional[str] = None
    in_school: Optional[str] = None
    home_activity: Optional[str] = None
    dinner_table_questions: Optional[list[str]] = None
    key_vocabulary: Optional[list[dict[str, Any]]] = None
    example_questions: Optional[list[str]] = None
    times_table_tip: Optional[str] = None
    teacher_note: Optional[str] = None
    unit_title: Optional[str] = None


class GenerateRequest(SQLModel):
    year_group: str = "year_2"
    term: str = "autumn"
    week_number: int = 1
    unit_title: str
