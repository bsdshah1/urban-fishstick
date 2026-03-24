#!/usr/bin/env python3
"""Seed the database with test users and sample digests.

Usage:
    python scripts/seed.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from api.auth import hash_password
from api.models.audit import AuditAction, AuditLog
from api.models.database import create_db_and_tables, engine
from api.models.digest import DigestStatus, WeeklyDigest
from api.models.user import User, UserRole


def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        # --- Users ---
        users_data = [
            {"email": "teacher@beaumont.sch.uk", "name": "Ms Clarke", "role": UserRole.teacher},
            {"email": "parent@beaumont.sch.uk", "name": "Sample Parent", "role": UserRole.parent},
            {"email": "admin@beaumont.sch.uk", "name": "School Admin", "role": UserRole.admin},
        ]
        created_users: dict[str, User] = {}
        for u in users_data:
            existing = session.exec(select(User).where(User.email == u["email"])).first()
            if existing:
                created_users[u["email"]] = existing
                print(f"  User already exists: {u['email']}")
            else:
                user = User(
                    email=u["email"],
                    hashed_password=hash_password("beaumont2024"),
                    name=u["name"],
                    role=u["role"],
                )
                session.add(user)
                session.flush()
                created_users[u["email"]] = user
                print(f"  Created user: {u['email']}")

        session.commit()

        teacher = session.exec(select(User).where(User.email == "teacher@beaumont.sch.uk")).first()

        # --- Sample Digests ---
        digests_data = [
            {
                "year_group": "year_2",
                "term": "autumn",
                "week_number": 1,
                "unit_title": "Place Value",
                "status": DigestStatus.published,
                "plain_english": (
                    "This week, Year 2 children are learning about place value — "
                    "understanding that the position of a digit tells us its value. "
                    "A number like 34 means 3 tens and 4 ones."
                ),
                "in_school": (
                    "Children use base-10 blocks (small cubes for ones, long rods for tens) "
                    "to build numbers and see how they're made. "
                    "They then draw the blocks before writing the number in digits."
                ),
                "home_activity": (
                    "Use coins or small objects to make a two-digit number together. "
                    "Group them into tens and ones — for example, 23 is two groups of ten and three leftover. "
                    "Take turns picking a number card and building it. No special equipment needed!"
                ),
                "dinner_table_questions": json.dumps([
                    "What does the '3' mean in the number 35?",
                    "Can you count to 100 by tens with me?",
                    "What number comes just before 50?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "tens", "definition": "Groups of ten. The number 30 has 3 tens."},
                    {"term": "ones", "definition": "Single units. The number 7 has 7 ones."},
                    {"term": "digit", "definition": "A single number symbol: 0, 1, 2, 3, 4, 5, 6, 7, 8 or 9."},
                    {"term": "place value", "definition": "The value of a digit based on its position in the number."},
                ]),
                "example_questions": json.dumps([
                    "What is the value of the 4 in the number 47?",
                    "Write the number that has 6 tens and 2 ones.",
                    "Which is greater: 53 or 35? How do you know?",
                ]),
                "times_table_tip": (
                    "This week focus on the 2 times table — "
                    "try counting in 2s while going up stairs or tidying toys."
                ),
                "teacher_note": "Great engagement in class this week — children loved the base-10 blocks!",
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "autumn",
                "week_number": 2,
                "unit_title": "Addition and Subtraction",
                "status": DigestStatus.approved,
                "plain_english": (
                    "Children are now using their place value knowledge to add and subtract "
                    "two-digit numbers. They are learning when to exchange ten ones for one ten."
                ),
                "in_school": (
                    "Lessons begin with concrete materials, then children draw bar models "
                    "before writing formal calculations. The focus is on understanding, not speed."
                ),
                "home_activity": (
                    "Play 'make 100' with a pack of cards. Draw two cards each and make a two-digit number. "
                    "Add them together — whoever gets closest to 100 without going over wins!"
                ),
                "dinner_table_questions": json.dumps([
                    "What is 34 + 25? Can you work it out in your head?",
                    "If I have 61 sweets and give away 28, how many do I have left?",
                    "What does 'exchange' mean in maths?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "add", "definition": "Put amounts together to find the total."},
                    {"term": "subtract", "definition": "Take an amount away to find what's left."},
                    {"term": "exchange", "definition": "Swap ten ones for one ten (or the other way round) when adding or subtracting."},
                    {"term": "total", "definition": "The answer when you add numbers together."},
                ]),
                "example_questions": json.dumps([
                    "34 + 25 = ?",
                    "61 − 28 = ?",
                    "I have 47 marbles. I get 36 more. How many do I have now?",
                ]),
                "times_table_tip": "Keep practising the 2 and 5 times tables — try counting in 5s while walking.",
                "teacher_note": None,
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "autumn",
                "week_number": 3,
                "unit_title": "Multiplication",
                "status": DigestStatus.draft,
                "plain_english": (
                    "This week introduces multiplication as repeated addition and equal groups. "
                    "Children will see that 3 × 4 means three groups of four."
                ),
                "in_school": (
                    "Children arrange counters into equal groups and write the matching multiplication. "
                    "They use arrays (rows and columns) to see commutativity: 3 × 4 = 4 × 3."
                ),
                "home_activity": (
                    "Arrange grapes, raisins, or pasta pieces into equal rows on a plate. "
                    "Write down the multiplication it shows. Can you write it two ways?"
                ),
                "dinner_table_questions": json.dumps([
                    "What does 3 × 5 mean? Can you show me with something?",
                    "How is multiplication like adding?",
                    "What times tables are you practising at school?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "multiply", "definition": "Find the total of equal groups."},
                    {"term": "groups of", "definition": "Equal sets. '3 groups of 4' means three sets of four."},
                    {"term": "array", "definition": "Objects arranged in rows and columns."},
                    {"term": "times table", "definition": "A list of multiplication facts for a given number."},
                ]),
                "example_questions": json.dumps([
                    "3 × 4 = ?",
                    "Draw an array to show 2 × 6.",
                    "There are 4 bags with 5 apples in each. How many apples altogether?",
                ]),
                "times_table_tip": "This week: focus on the 10 times table. Anything × 10 just gets a zero on the end!",
                "teacher_note": None,
                "generated_by_ai": True,
            },
        ]

        for d in digests_data:
            existing = session.exec(
                select(WeeklyDigest).where(
                    WeeklyDigest.year_group == d["year_group"],
                    WeeklyDigest.week_number == d["week_number"],
                )
            ).first()
            if existing:
                print(f"  Digest already exists: Week {d['week_number']} ({d['unit_title']})")
                continue

            digest = WeeklyDigest(
                year_group=d["year_group"],
                term=d["term"],
                week_number=d["week_number"],
                unit_title=d["unit_title"],
                status=d["status"],
                plain_english=d["plain_english"],
                in_school=d["in_school"],
                home_activity=d["home_activity"],
                dinner_table_questions_json=d["dinner_table_questions"],
                key_vocabulary_json=d["key_vocabulary"],
                example_questions_json=d["example_questions"],
                times_table_tip=d["times_table_tip"],
                teacher_note=d.get("teacher_note"),
                generated_by_ai=d.get("generated_by_ai", False),
            )
            if d["status"] in (DigestStatus.approved, DigestStatus.published) and teacher:
                from datetime import datetime
                digest.approved_at = datetime.utcnow()
                digest.approved_by_id = teacher.id
            if d["status"] == DigestStatus.published:
                from datetime import datetime
                digest.published_at = datetime.utcnow()

            session.add(digest)
            session.flush()

            # Audit entries
            if teacher:
                if d.get("generated_by_ai"):
                    session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.generated))
                if d["status"] in (DigestStatus.approved, DigestStatus.published):
                    session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.approved))
                if d["status"] == DigestStatus.published:
                    session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.published))

            print(f"  Created digest: Week {d['week_number']} — {d['unit_title']} [{d['status']}]")

        session.commit()
        print("\nSeed complete.")
        print("  Login: teacher@beaumont.sch.uk / beaumont2024")
        print("  Login: parent@beaumont.sch.uk  / beaumont2024")
        print("  Login: admin@beaumont.sch.uk   / beaumont2024")


if __name__ == "__main__":
    seed()
