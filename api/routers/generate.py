"""AI generation endpoint."""

from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from api.auth import require_role
from api.models.audit import AuditAction, AuditLog
from api.models.database import get_session
from api.models.digest import DigestRead, GenerateRequest, WeeklyDigest
from api.models.user import User, UserRole
from services.ai_generator import generate_weekly_digest
from services.curriculum_adapter import get_curriculum_context

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("", response_model=DigestRead, status_code=201)
def generate_digest(
    body: GenerateRequest,
    current_user: User = Depends(require_role(UserRole.teacher, UserRole.admin)),
    session: Session = Depends(get_session),
) -> DigestRead:
    context = get_curriculum_context(body.year_group, body.unit_title)
    data = generate_weekly_digest(
        year_group=body.year_group,
        term=body.term,
        week_number=body.week_number,
        unit_title=body.unit_title,
        curriculum_context=context,
    )

    digest = WeeklyDigest(
        year_group=body.year_group,
        term=body.term,
        week_number=body.week_number,
        unit_title=body.unit_title,
        plain_english=data.get("plain_english", ""),
        in_school=data.get("in_school", ""),
        home_activity=data.get("home_activity", ""),
        dinner_table_questions_json=json.dumps(data.get("dinner_table_questions", [])),
        key_vocabulary_json=json.dumps(data.get("key_vocabulary", [])),
        example_questions_json=json.dumps(data.get("example_questions", [])),
        times_table_tip=data.get("times_table_tip", ""),
        teacher_note=None,
        generated_by_ai=True,
    )
    session.add(digest)
    session.flush()  # get id before audit log

    session.add(AuditLog(
        digest_id=digest.id,
        user_id=current_user.id,
        action=AuditAction.generated,
    ))
    session.commit()
    session.refresh(digest)
    return DigestRead.from_orm(digest)
