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
                    WeeklyDigest.term == d["term"],
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

        # --- Summer term digests ---
        summer_digests = [
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 1,
                "unit_title": "Halves and Quarters",
                "status": DigestStatus.published,
                "plain_english": (
                    "This week Year 2 children are beginning to explore fractions. "
                    "They are learning that a fraction is an equal part of a whole — "
                    "so a half means dividing something into exactly two equal pieces, "
                    "and a quarter means dividing into four equal pieces."
                ),
                "in_school": (
                    "Children start by folding paper squares and circles in half, then in quarters, "
                    "checking that both sides match exactly. They colour one half or one quarter, "
                    "and learn to write these as ½ and ¼. They also share a set of objects equally — "
                    "for example, 8 counters shared between 2 children gives ½ of 8 = 4."
                ),
                "home_activity": (
                    "Fold a piece of paper in half — does each part look exactly the same? "
                    "Now fold it again to make quarters. Colour one quarter a different colour. "
                    "You can also try cutting an apple or sandwich in half and talking about "
                    "whether both pieces are equal. If one is bigger, it's not a true half!"
                ),
                "dinner_table_questions": json.dumps([
                    "If I cut this pizza into 2 equal pieces, what fraction is each piece?",
                    "Can you show me half of 6 using these grapes?",
                    "Is this piece of bread a half? How do you know?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "fraction", "definition": "An equal part of a whole shape or set of objects."},
                    {"term": "half (½)", "definition": "One of two equal parts. Half of 8 is 4."},
                    {"term": "quarter (¼)", "definition": "One of four equal parts. A quarter of 8 is 2."},
                    {"term": "equal parts", "definition": "Parts that are exactly the same size."},
                    {"term": "whole", "definition": "The complete shape or amount before it is split."},
                ]),
                "example_questions": json.dumps([
                    "Shade ½ of this rectangle.",
                    "What is ¼ of 12?",
                    "Tom cuts a cake into 4 pieces. Are they quarters? Only if they are ___.",
                    "Circle the shape that shows one quarter shaded correctly.",
                ]),
                "times_table_tip": (
                    "Fractions and the 2 times table go hand in hand! "
                    "Half of any even number is just that number in the 2 times table — "
                    "half of 10 is 5, half of 14 is 7. Try it together!"
                ),
                "teacher_note": "Children were brilliant at the folding activity — lots of great discussion about what 'equal' really means.",
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 2,
                "unit_title": "Thirds and Unit Fractions",
                "status": DigestStatus.published,
                "plain_english": (
                    "Children are now extending their fraction knowledge to thirds — "
                    "dividing shapes and sets into three equal parts. "
                    "They are also comparing unit fractions (fractions with a 1 on top, like ½, ⅓, ¼) "
                    "and discovering that the larger the bottom number, the smaller each piece is."
                ),
                "in_school": (
                    "Children fold strips of paper into three equal parts to make thirds, "
                    "then compare strips folded into halves, thirds, and quarters side by side. "
                    "They use a 'fraction wall' — rows of strips divided into different fractions — "
                    "to see which fraction is biggest. This visual approach helps them understand "
                    "that ½ > ⅓ > ¼ without needing to calculate."
                ),
                "home_activity": (
                    "Make a simple fraction wall at home! Cut three strips of paper the same length. "
                    "Leave one whole, fold the second in half, and fold the third into three equal parts. "
                    "Line them up and ask: which piece is biggest? Which is smallest? "
                    "Can your child explain why — even though 3 is bigger than 2, a third is smaller than a half?"
                ),
                "dinner_table_questions": json.dumps([
                    "If we share this chocolate bar equally between 3 people, what fraction does each person get?",
                    "Which is bigger — half a pizza or a third of a pizza? How do you know?",
                    "Can you name three fractions that all have a 1 on top?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "third (⅓)", "definition": "One of three equal parts. A third of 9 is 3."},
                    {"term": "unit fraction", "definition": "A fraction with 1 as the top number, like ½, ⅓ or ¼."},
                    {"term": "numerator", "definition": "The top number of a fraction — how many parts we have."},
                    {"term": "denominator", "definition": "The bottom number — how many equal parts the whole is split into."},
                    {"term": "fraction wall", "definition": "A diagram showing fractions as rows of equal strips to compare sizes."},
                ]),
                "example_questions": json.dumps([
                    "Shade ⅓ of this shape.",
                    "What is ⅓ of 9? What is ¼ of 12?",
                    "Put these fractions in order, smallest first: ¼, ½, ⅓",
                    "True or false: ⅓ is bigger than ½. Explain how you know.",
                ]),
                "times_table_tip": (
                    "Finding a third of a number uses the 3 times table in reverse! "
                    "A third of 12 is 4 because 4 × 3 = 12. "
                    "Practise: a third of 6, a third of 9, a third of 15."
                ),
                "teacher_note": None,
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 3,
                "unit_title": "Telling the Time — O'Clock and Half Past",
                "status": DigestStatus.published,
                "plain_english": (
                    "This week children are learning to read and write the time on both analogue "
                    "(the round clock with hands) and digital clocks. "
                    "They are focusing on o'clock — when the minute hand points straight up to 12 — "
                    "and half past — when the minute hand points straight down to 6."
                ),
                "in_school": (
                    "Children use clocks with moveable hands to practise setting times and reading them. "
                    "They match analogue clock faces to digital times (e.g. 3:00 and 3:30), "
                    "draw hands onto blank clock faces, and sequence events in a day "
                    "(breakfast at 8 o'clock, school at 9 o'clock, lunch at 12 o'clock). "
                    "The language of 'past' is introduced — half past 3 means 30 minutes after 3."
                ),
                "home_activity": (
                    "Go on a 'time hunt' at home! Find every clock or watch you can — "
                    "on the oven, microwave, phone, or wall. Each time you spot one, "
                    "ask your child what time it shows and whether it's o'clock or half past. "
                    "You can also draw a blank clock face and take turns setting a time for the other person to read."
                ),
                "dinner_table_questions": json.dumps([
                    "What time did we sit down for dinner? Is it o'clock or half past?",
                    "Where does the minute hand point at half past?",
                    "What will happen at half past 7 tonight? (bedtime, bath time, etc.)",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "analogue clock", "definition": "A clock with a round face and two hands that move round."},
                    {"term": "digital clock", "definition": "A clock that shows the time as numbers, like 3:30."},
                    {"term": "minute hand", "definition": "The long hand on a clock. It moves all the way round in 60 minutes."},
                    {"term": "hour hand", "definition": "The short hand on a clock. It points to the hour."},
                    {"term": "half past", "definition": "30 minutes after the hour. The minute hand points to the 6."},
                ]),
                "example_questions": json.dumps([
                    "Draw the hands on a clock to show 4 o'clock.",
                    "What time does this clock show? (minute hand on 6, hour hand between 2 and 3)",
                    "Write the digital time for half past 7.",
                    "A film starts at 2 o'clock and lasts 1 hour. What time does it finish?",
                ]),
                "times_table_tip": (
                    "The clock is secretly a times table tool! "
                    "Counting round the clock in 5s shows the 5 times table: 5, 10, 15, 20… all the way to 60. "
                    "Each number on the clock face is 5 more minutes."
                ),
                "teacher_note": "We used giant floor clocks in the hall — children loved becoming the 'minute hand' and 'hour hand' themselves!",
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 4,
                "unit_title": "Quarter Past and Quarter To",
                "status": DigestStatus.published,
                "plain_english": (
                    "Children are building on last week's time work to read quarter past and quarter to. "
                    "Quarter past means 15 minutes after the hour (the minute hand at the 3), "
                    "and quarter to means 15 minutes before the next hour (the minute hand at the 9). "
                    "This is trickier because 'quarter to 4' is actually closer to 4 than to 3!"
                ),
                "in_school": (
                    "Children use fraction language they already know — quarters of a circle — "
                    "to understand the clock face as divided into four equal parts. "
                    "They learn that one full turn of the minute hand = 1 hour = 60 minutes, "
                    "and a quarter turn = 15 minutes. "
                    "They practise ordering times and filling in timetables with quarter hours."
                ),
                "home_activity": (
                    "Play 'Beat the Clock'! Set a clock or timer to quarter past an hour "
                    "and ask your child to name the time before it changes. "
                    "Then try quarter to. A great way to practise is to narrate real times throughout the day: "
                    "'It's quarter to 6 — that's 15 minutes until 6 o'clock, which is dinner time!'"
                ),
                "dinner_table_questions": json.dumps([
                    "If it's quarter past 5, how many minutes until half past 5?",
                    "Quarter to 8 — what hour is it nearly? How long until 8 o'clock?",
                    "Can you draw a clock showing quarter past 3?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "quarter past", "definition": "15 minutes after the hour. The minute hand points to the 3."},
                    {"term": "quarter to", "definition": "15 minutes before the next hour. The minute hand points to the 9."},
                    {"term": "minutes", "definition": "There are 60 minutes in one hour."},
                    {"term": "duration", "definition": "How long something lasts. A film might have a duration of 2 hours."},
                ]),
                "example_questions": json.dumps([
                    "What time is shown? (minute hand on 3, hour hand just past 7) → Quarter past 7",
                    "Draw a clock showing quarter to 9.",
                    "A lesson starts at quarter past 10 and lasts 45 minutes. What time does it end?",
                    "Order these times: quarter to 3, half past 2, quarter past 2, 2 o'clock.",
                ]),
                "times_table_tip": (
                    "Quarter past uses the number 15, quarter to uses 45. "
                    "Both appear in the 5 times table! "
                    "Try counting on in 5s from 0 and spot where 15 and 45 fall."
                ),
                "teacher_note": None,
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 5,
                "unit_title": "Tally Charts and Pictograms",
                "status": DigestStatus.published,
                "plain_english": (
                    "This week children are exploring statistics — collecting data and showing it in different ways. "
                    "They are learning to use tally marks (groups of five, using a diagonal line for the fifth) "
                    "to count quickly, and to show data as a pictogram — a chart that uses pictures or symbols "
                    "where each symbol represents one (or more) items."
                ),
                "in_school": (
                    "Children conduct simple surveys in class — favourite fruit, pets at home, "
                    "ways to travel to school — recording results in tally charts. "
                    "They then turn their tally charts into pictograms, choosing a symbol for each data set. "
                    "They practise reading pictograms to answer questions like 'How many more children chose X than Y?'"
                ),
                "home_activity": (
                    "Do a family survey! Pick a question — 'What's your favourite colour?' or 'How many windows are in each room?' "
                    "Record the results using tally marks on a piece of paper. "
                    "Then make a pictogram together — draw a simple picture for each answer "
                    "and line them up in rows to make a chart. What does your data show?"
                ),
                "dinner_table_questions": json.dumps([
                    "How many tally marks make a group of 5? Why do we bundle them like that?",
                    "If our pictogram shows 4 apples and each apple means 2 children, how many children chose apples?",
                    "What question could we ask at school to collect interesting data?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "data", "definition": "Information we collect by counting, measuring, or asking questions."},
                    {"term": "tally chart", "definition": "A way of counting using marks — every fifth mark crosses the previous four."},
                    {"term": "pictogram", "definition": "A chart that uses pictures or symbols to represent data."},
                    {"term": "key", "definition": "In a pictogram, the key tells you what each symbol represents."},
                    {"term": "frequency", "definition": "How many times something happens or is chosen."},
                ]),
                "example_questions": json.dumps([
                    "A tally chart shows: cats: ||||, dogs: |||| ||, fish: ||. How many children have dogs?",
                    "In a pictogram, each star = 2 children. There are 5 stars for 'football'. How many children chose football?",
                    "How many more children chose dogs than cats?",
                    "Which is the most popular pet? How can you tell from the chart?",
                ]),
                "times_table_tip": (
                    "Tally charts count in 5s, which is perfect for practising the 5 times table! "
                    "Each bundle of tallies is 5. Count the bundles and multiply by 5 to get the total quickly."
                ),
                "teacher_note": "Children loved collecting real data about each other — there were some very lively debates about favourite flavours!",
                "generated_by_ai": False,
            },
            {
                "year_group": "year_2",
                "term": "summer",
                "week_number": 6,
                "unit_title": "Position and Direction",
                "status": DigestStatus.published,
                "plain_english": (
                    "In the final block of Year 2, children are learning to describe and follow directions. "
                    "They use language like left, right, forwards, backwards, and learn about quarter turns, "
                    "half turns, and full turns — connecting their knowledge of fractions to movement in space. "
                    "They also use positional language: above, below, beside, between."
                ),
                "in_school": (
                    "Children follow and give directions on a grid map, moving a counter or robot step by step. "
                    "They describe turns using the language of clockwise and anti-clockwise, "
                    "and connect a quarter turn (90°) to the quarter of a circle they know from fractions. "
                    "They look at patterns and create their own using turns and reflections on squared paper."
                ),
                "home_activity": (
                    "Play a directions game in your home or garden! "
                    "Start at one point and give your child instructions: '3 steps forward, turn right, 2 steps forward.' "
                    "Can they reach the target? Then swap — let them give you directions. "
                    "Try using grid paper to draw a simple map and plan a route using arrows."
                ),
                "dinner_table_questions": json.dumps([
                    "If you face the front door and turn right, what do you see?",
                    "How many quarter turns make a half turn? How many make a full turn?",
                    "Can you describe how to get from the kitchen to your bedroom using directions?",
                ]),
                "key_vocabulary": json.dumps([
                    {"term": "clockwise", "definition": "Turning in the same direction as clock hands move — to the right."},
                    {"term": "anti-clockwise", "definition": "Turning in the opposite direction to clock hands — to the left."},
                    {"term": "quarter turn", "definition": "A turn of 90 degrees — like the corner of a square."},
                    {"term": "half turn", "definition": "A turn of 180 degrees — you end up facing the opposite direction."},
                    {"term": "full turn", "definition": "A complete 360-degree turn — you end up facing the same way you started."},
                ]),
                "example_questions": json.dumps([
                    "A robot faces North and makes a quarter turn clockwise. Which direction does it now face?",
                    "Describe the route from A to B on this grid using: steps forward, turn left/right.",
                    "How many quarter turns clockwise equal one half turn?",
                    "Draw a shape that has a line of symmetry.",
                ]),
                "times_table_tip": (
                    "You're doing brilliantly — keep up the 2, 5, and 10 times tables this summer! "
                    "Try the 3 times table too: 3, 6, 9, 12, 15… count in 3s while bouncing a ball."
                ),
                "teacher_note": "A fantastic end to Year 2 — the children have grown so much in confidence this year. Well done to all our families for supporting learning at home!",
                "generated_by_ai": False,
            },
        ]

        for d in summer_digests:
            existing = session.exec(
                select(WeeklyDigest).where(
                    WeeklyDigest.year_group == d["year_group"],
                    WeeklyDigest.term == d["term"],
                    WeeklyDigest.week_number == d["week_number"],
                )
            ).first()
            if existing:
                print(f"  Digest already exists: Summer Week {d['week_number']} ({d['unit_title']})")
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
            if teacher:
                from datetime import datetime
                digest.approved_at = datetime.utcnow()
                digest.approved_by_id = teacher.id
                digest.published_at = datetime.utcnow()

            session.add(digest)
            session.flush()

            if teacher:
                session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.approved))
                session.add(AuditLog(digest_id=digest.id, user_id=teacher.id, action=AuditAction.published))

            print(f"  Created digest: Summer Week {d['week_number']} — {d['unit_title']} [published]")

        session.commit()
        print("\nSeed complete.")
        print("  Login: teacher@beaumont.sch.uk / beaumont2024")
        print("  Login: parent@beaumont.sch.uk  / beaumont2024")
        print("  Login: admin@beaumont.sch.uk   / beaumont2024")


if __name__ == "__main__":
    seed()
