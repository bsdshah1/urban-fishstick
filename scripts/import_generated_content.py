#!/usr/bin/env python3
"""Import all generated JSON digest files into the database as published content.

Usage:
    python scripts/import_generated_content.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from api.auth import hash_password
from api.models.database import create_db_and_tables, engine
from api.models.audit import AuditAction, AuditLog
from api.models.digest import DigestStatus, WeeklyDigest
from api.models.user import User, UserRole

GENERATED_DIR = Path(__file__).resolve().parent.parent / "app" / "content" / "generated" / "digests"


def ensure_users(session: Session) -> User:
    users_data = [
        {"email": "teacher@beaumont.sch.uk", "name": "Ms Clarke", "role": UserRole.teacher},
        {"email": "parent@beaumont.sch.uk", "name": "Sample Parent", "role": UserRole.parent},
        {"email": "admin@beaumont.sch.uk", "name": "School Admin", "role": UserRole.admin},
    ]
    for u in users_data:
        existing = session.exec(select(User).where(User.email == u["email"])).first()
        if not existing:
            user = User(
                email=u["email"],
                hashed_password=hash_password("beaumont2024"),
                name=u["name"],
                role=u["role"],
            )
            session.add(user)
            print(f"  Created user: {u['email']}")
    session.commit()
    return session.exec(select(User).where(User.email == "teacher@beaumont.sch.uk")).first()


def import_digests(session: Session, teacher: User) -> None:
    # Group files by (year_group, term) to assign sequential week numbers
    term_files: dict[tuple[str, str], list[Path]] = {}
    for json_file in sorted(GENERATED_DIR.rglob("*.json")):
        parts = json_file.parts
        # path: .../digests/{year_group}/{term_id}/{block_id}.json
        if len(parts) < 3:
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  Skipping {json_file.name}: {e}")
            continue
        year_group = data.get("year_group", "")
        term = data.get("term", "")
        key = (year_group, term)
        term_files.setdefault(key, []).append(json_file)

    total_created = 0
    total_skipped = 0

    for (year_group, term), files in sorted(term_files.items()):
        for week_num, json_file in enumerate(files, start=1):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            content = data.get("content", {})

            # Check if already exists (by year_group + term + week_number)
            existing = session.exec(
                select(WeeklyDigest).where(
                    WeeklyDigest.year_group == year_group,
                    WeeklyDigest.term == term,
                    WeeklyDigest.week_number == week_num,
                )
            ).first()

            if existing:
                total_skipped += 1
                continue

            unit_title = data.get("unit_title") or data.get("block_name") or "Maths"

            dtq = content.get("dinner_table_questions", [])
            kv = content.get("key_vocabulary", [])
            eq = content.get("example_questions", [])

            now = datetime.utcnow()
            digest = WeeklyDigest(
                year_group=year_group,
                term=term,
                week_number=week_num,
                unit_title=unit_title,
                status=DigestStatus.published,
                plain_english=content.get("plain_english", ""),
                in_school=content.get("in_school", ""),
                home_activity=content.get("home_activity", ""),
                dinner_table_questions_json=json.dumps(dtq if isinstance(dtq, list) else []),
                key_vocabulary_json=json.dumps(kv if isinstance(kv, list) else []),
                example_questions_json=json.dumps(eq if isinstance(eq, list) else []),
                times_table_tip=content.get("times_table_tip", ""),
                teacher_note=None,
                generated_by_ai=True,
                approved_at=now,
                published_at=now,
                approved_by_id=teacher.id if teacher else None,
            )
            session.add(digest)
            session.flush()

            if teacher:
                session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.generated))
                session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.approved))
                session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.published))

            total_created += 1
            print(f"  [{year_group} / {term} / week {week_num}] {unit_title}")

        session.commit()

    print(f"\nDone: {total_created} created, {total_skipped} already existed.")


def main() -> None:
    print("Creating database tables…")
    create_db_and_tables()

    with Session(engine) as session:
        print("Ensuring users…")
        teacher = ensure_users(session)
        print("Importing generated digests…")
        import_digests(session, teacher)


if __name__ == "__main__":
    main()
