"""Digest CRUD and workflow endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from api.auth import get_current_user, require_role
from api.models.audit import AuditAction, AuditLog
from api.models.database import get_session
from api.models.digest import DigestRead, DigestStatus, DigestUpdate, WeeklyDigest
from api.models.user import User, UserRole

router = APIRouter(prefix="/api/digests", tags=["digests"])


def _to_read(d: WeeklyDigest) -> DigestRead:
    return DigestRead.from_orm(d)


def _record_audit(
    session: Session,
    digest_id: int,
    user_id: int,
    action: AuditAction,
    note: Optional[str] = None,
) -> None:
    session.add(AuditLog(digest_id=digest_id, user_id=user_id, action=action, note=note))


@router.get("", response_model=list[DigestRead])
def list_digests(
    session: Session = Depends(get_session),
) -> list[DigestRead]:
    """Public endpoint — returns only published digests."""
    stmt = select(WeeklyDigest).where(WeeklyDigest.status == DigestStatus.published)
    results = session.exec(stmt.order_by(WeeklyDigest.week_number.desc())).all()
    return [_to_read(d) for d in results]


@router.get("/{digest_id}", response_model=DigestRead)
def get_digest(
    digest_id: int,
    session: Session = Depends(get_session),
) -> DigestRead:
    """Public endpoint — only published digests are visible."""
    digest = session.get(WeeklyDigest, digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    if digest.status != DigestStatus.published:
        raise HTTPException(status_code=404, detail="Digest not found")
    return _to_read(digest)


@router.patch("/{digest_id}", response_model=DigestRead)
def update_digest(
    digest_id: int,
    body: DigestUpdate,
    current_user: User = Depends(require_role(UserRole.teacher, UserRole.admin)),
    session: Session = Depends(get_session),
) -> DigestRead:
    digest = session.get(WeeklyDigest, digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        if field == "dinner_table_questions":
            digest.dinner_table_questions_json = json.dumps(value)
        elif field == "key_vocabulary":
            digest.key_vocabulary_json = json.dumps(value)
        elif field == "example_questions":
            digest.example_questions_json = json.dumps(value)
        else:
            setattr(digest, field, value)

    digest.updated_at = datetime.utcnow()
    session.add(digest)
    _record_audit(session, digest_id, current_user.id, AuditAction.edited)
    session.commit()
    session.refresh(digest)
    return _to_read(digest)


@router.post("/{digest_id}/approve", response_model=DigestRead)
def approve_digest(
    digest_id: int,
    current_user: User = Depends(require_role(UserRole.teacher, UserRole.admin)),
    session: Session = Depends(get_session),
) -> DigestRead:
    digest = session.get(WeeklyDigest, digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    digest.status = DigestStatus.approved
    digest.approved_at = datetime.utcnow()
    digest.approved_by_id = current_user.id
    digest.updated_at = datetime.utcnow()
    session.add(digest)
    _record_audit(session, digest_id, current_user.id, AuditAction.approved)
    session.commit()
    session.refresh(digest)
    return _to_read(digest)


@router.post("/{digest_id}/publish", response_model=DigestRead)
def publish_digest(
    digest_id: int,
    current_user: User = Depends(require_role(UserRole.teacher, UserRole.admin)),
    session: Session = Depends(get_session),
) -> DigestRead:
    digest = session.get(WeeklyDigest, digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    action = AuditAction.republished if digest.status == DigestStatus.published else AuditAction.published
    digest.status = DigestStatus.published
    digest.published_at = datetime.utcnow()
    digest.updated_at = datetime.utcnow()
    session.add(digest)
    _record_audit(session, digest_id, current_user.id, action)
    session.commit()
    session.refresh(digest)
    return _to_read(digest)


class FlagRequest(BaseModel):
    note: Optional[str] = None


@router.post("/{digest_id}/flag", response_model=DigestRead)
def flag_digest(
    digest_id: int,
    body: FlagRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DigestRead:
    digest = session.get(WeeklyDigest, digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    digest.status = DigestStatus.flagged
    digest.updated_at = datetime.utcnow()
    session.add(digest)
    _record_audit(session, digest_id, current_user.id, AuditAction.flagged, note=body.note)
    session.commit()
    session.refresh(digest)
    return _to_read(digest)
