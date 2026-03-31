"""AI digest generator using the Anthropic Claude API."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ── Vocabulary bank ──────────────────────────────────────────────────────────
# Keyed by topic keyword (lowercase). Each entry is a list of dicts with
# "term" and "definition" suitable for the key_vocabulary digest field.
_VOCAB_BANK: dict[str, list[dict]] = {
    "place value": [
        {"term": "digit", "definition": "One of the symbols 0–9 used to write a number."},
        {"term": "place value", "definition": "The value of a digit based on its position — units, tens, hundreds, and so on."},
        {"term": "partition", "definition": "Split a number into its parts — e.g. 347 = 300 + 40 + 7."},
        {"term": "round", "definition": "Give an approximate value to the nearest 10, 100, etc."},
        {"term": "estimate", "definition": "Make a sensible guess at an answer before you calculate."},
    ],
    "addition": [
        {"term": "sum", "definition": "The result of adding two or more numbers together."},
        {"term": "column addition", "definition": "A written method where numbers are lined up in columns to add."},
        {"term": "exchange", "definition": "Swap 10 ones for 1 ten (or 10 tens for 1 hundred) when adding."},
        {"term": "addend", "definition": "A number being added to another."},
        {"term": "inverse", "definition": "The opposite operation — addition and subtraction are inverses of each other."},
    ],
    "subtraction": [
        {"term": "difference", "definition": "The result of subtracting one number from another."},
        {"term": "column subtraction", "definition": "A written method where numbers are lined up in columns to subtract."},
        {"term": "exchange", "definition": "Swap 1 ten for 10 ones when you need to subtract a larger digit."},
        {"term": "minuend", "definition": "The number you start with when you subtract."},
        {"term": "inverse", "definition": "The opposite operation — if you know 12 − 5 = 7, you also know 7 + 5 = 12."},
    ],
    "multiplication": [
        {"term": "product", "definition": "The result of multiplying two numbers together."},
        {"term": "factor", "definition": "A number that divides exactly into another number."},
        {"term": "multiple", "definition": "A number in a times-table sequence — e.g. multiples of 4 are 4, 8, 12, 16…"},
        {"term": "array", "definition": "Objects arranged in equal rows and columns to show multiplication."},
        {"term": "formal method", "definition": "A written, columnar way of setting out a calculation."},
    ],
    "division": [
        {"term": "quotient", "definition": "The result when one number is divided by another."},
        {"term": "divisor", "definition": "The number you are dividing by."},
        {"term": "remainder", "definition": "What is left over after dividing, when a number does not divide exactly."},
        {"term": "factor", "definition": "A number that divides exactly into another number."},
        {"term": "inverse", "definition": "The opposite operation — multiplication and division are inverses of each other."},
    ],
    "fractions": [
        {"term": "numerator", "definition": "The top number in a fraction — shows how many equal parts we have."},
        {"term": "denominator", "definition": "The bottom number in a fraction — shows how many equal parts the whole is split into."},
        {"term": "equivalent fraction", "definition": "Fractions that look different but have the same value — e.g. ½ = 2/4."},
        {"term": "unit fraction", "definition": "A fraction with 1 as the numerator — such as ½, ⅓, ¼."},
        {"term": "mixed number", "definition": "A number with a whole number part and a fraction part — e.g. 2½."},
    ],
    "decimals": [
        {"term": "decimal point", "definition": "The dot separating the whole number part from the fractional part — e.g. 3.7."},
        {"term": "tenths", "definition": "The first digit after the decimal point — each tenth is one part out of ten."},
        {"term": "hundredths", "definition": "The second digit after the decimal point — one part out of a hundred."},
        {"term": "equivalent", "definition": "Having the same value — e.g. 0.5 = ½ = 50%."},
        {"term": "round", "definition": "Give a decimal to a certain number of decimal places."},
    ],
    "percentage": [
        {"term": "percentage", "definition": "A number shown as parts out of 100, written with a % sign."},
        {"term": "proportion", "definition": "How much of something there is relative to the whole."},
        {"term": "equivalent", "definition": "Equal in value — e.g. 50% = 0.5 = ½."},
        {"term": "convert", "definition": "Change between percentages, decimals, and fractions."},
        {"term": "per cent", "definition": "Out of a hundred — 'per' means for each, 'cent' means hundred."},
    ],
    "ratio": [
        {"term": "ratio", "definition": "A comparison of two quantities, written as 1:2 — for every 1 of one thing, there are 2 of another."},
        {"term": "proportion", "definition": "Part of a whole — often written as a fraction or percentage."},
        {"term": "scale factor", "definition": "The number you multiply all lengths by when scaling a shape up or down."},
        {"term": "simplify", "definition": "Write a ratio using the smallest possible whole numbers — e.g. 4:6 simplifies to 2:3."},
        {"term": "equivalent ratio", "definition": "Ratios that describe the same relationship — e.g. 1:2 and 3:6 are equivalent."},
    ],
    "algebra": [
        {"term": "variable", "definition": "A letter used to stand for an unknown number — such as n or x."},
        {"term": "equation", "definition": "A statement showing two things are equal — e.g. 2n + 3 = 11."},
        {"term": "expression", "definition": "A combination of numbers, letters, and operations — e.g. 3n + 5."},
        {"term": "formula", "definition": "A rule written with symbols — such as area = length × width."},
        {"term": "substitute", "definition": "Replace a variable with a number to work out the value of an expression."},
    ],
    "geometry": [
        {"term": "vertex", "definition": "A corner of a shape where two or more edges meet. Plural: vertices."},
        {"term": "edge", "definition": "A straight line where two faces of a 3-D shape meet."},
        {"term": "face", "definition": "A flat surface on a 3-D shape."},
        {"term": "polygon", "definition": "A closed 2-D shape with straight sides — e.g. triangle, square, hexagon."},
        {"term": "parallel", "definition": "Lines that are always the same distance apart and never meet."},
    ],
    "shape": [
        {"term": "2-D shape", "definition": "A flat shape with length and width but no thickness — e.g. triangle, circle."},
        {"term": "3-D shape", "definition": "A solid shape with length, width, and height — e.g. cube, sphere, cone."},
        {"term": "symmetry", "definition": "When one half of a shape is a mirror image of the other."},
        {"term": "right angle", "definition": "An angle of exactly 90° — the same as the corner of a square."},
        {"term": "perpendicular", "definition": "Lines that meet at a right angle (90°)."},
    ],
    "angles": [
        {"term": "angle", "definition": "The amount of turn between two lines, measured in degrees (°)."},
        {"term": "right angle", "definition": "An angle of exactly 90°."},
        {"term": "acute angle", "definition": "An angle less than 90°."},
        {"term": "obtuse angle", "definition": "An angle between 90° and 180°."},
        {"term": "reflex angle", "definition": "An angle greater than 180°."},
    ],
    "perimeter": [
        {"term": "perimeter", "definition": "The total distance around the outside edge of a shape."},
        {"term": "length", "definition": "How long something is from one end to the other."},
        {"term": "width", "definition": "How wide something is from side to side."},
        {"term": "centimetre (cm)", "definition": "A unit of length — 100 cm = 1 metre."},
        {"term": "metre (m)", "definition": "A unit of length — 1000 m = 1 kilometre."},
    ],
    "area": [
        {"term": "area", "definition": "The amount of space inside a 2-D shape, measured in square units."},
        {"term": "square centimetre (cm²)", "definition": "A unit for measuring area — the space of a 1 cm × 1 cm square."},
        {"term": "length", "definition": "How long a side of the shape is."},
        {"term": "width", "definition": "How wide the shape is."},
        {"term": "formula", "definition": "A rule — for a rectangle, area = length × width."},
    ],
    "volume": [
        {"term": "volume", "definition": "The amount of space a 3-D shape takes up, measured in cubic units."},
        {"term": "capacity", "definition": "The maximum amount a container can hold."},
        {"term": "cubic centimetre (cm³)", "definition": "A unit for measuring volume — a 1 cm × 1 cm × 1 cm cube."},
        {"term": "litre (l)", "definition": "A unit of capacity — 1 litre = 1000 millilitres."},
        {"term": "millilitre (ml)", "definition": "A small unit of capacity — 1000 ml = 1 litre."},
    ],
    "length": [
        {"term": "length", "definition": "How long something is from one end to the other."},
        {"term": "millimetre (mm)", "definition": "A very small unit of length — 10 mm = 1 cm."},
        {"term": "centimetre (cm)", "definition": "A unit of length — 100 cm = 1 metre."},
        {"term": "metre (m)", "definition": "A unit of length — 1000 m = 1 kilometre."},
        {"term": "estimate", "definition": "Make a sensible guess at a measurement before you measure it."},
    ],
    "mass": [
        {"term": "mass", "definition": "How heavy an object is — measured in grams or kilograms."},
        {"term": "gram (g)", "definition": "A unit of mass — 1000 g = 1 kg."},
        {"term": "kilogram (kg)", "definition": "A unit of mass — 1 kg = 1000 g."},
        {"term": "balance", "definition": "When both sides of a scale have equal mass."},
        {"term": "compare", "definition": "Find out which object is heavier or lighter."},
    ],
    "capacity": [
        {"term": "capacity", "definition": "The maximum amount a container can hold."},
        {"term": "volume", "definition": "The amount of liquid in a container."},
        {"term": "millilitre (ml)", "definition": "A small unit of capacity — 1000 ml = 1 litre."},
        {"term": "litre (l)", "definition": "A unit of capacity — 1 litre = 1000 ml."},
        {"term": "full / empty / half-full", "definition": "Words used to describe how much a container holds."},
    ],
    "time": [
        {"term": "second", "definition": "A small unit of time — 60 seconds = 1 minute."},
        {"term": "minute", "definition": "A unit of time — 60 minutes = 1 hour."},
        {"term": "hour", "definition": "A unit of time — 24 hours = 1 day."},
        {"term": "analogue", "definition": "A clock with hands that show the time on a circular face."},
        {"term": "duration", "definition": "How long something takes from start to finish."},
    ],
    "money": [
        {"term": "pence (p)", "definition": "The smaller unit of British money — 100p = £1."},
        {"term": "pound (£)", "definition": "The main unit of British money."},
        {"term": "change", "definition": "The money you get back when you pay more than something costs."},
        {"term": "total", "definition": "The overall amount when prices are added together."},
        {"term": "decimal point", "definition": "The dot in a money amount separating pounds from pence — e.g. £2.50."},
    ],
    "statistics": [
        {"term": "data", "definition": "Information collected through counting, measuring, or surveying."},
        {"term": "tally", "definition": "A way of counting using marks in groups of five."},
        {"term": "frequency", "definition": "How often something occurs in a set of data."},
        {"term": "bar chart", "definition": "A graph that uses bars to show and compare amounts."},
        {"term": "axis", "definition": "The horizontal or vertical line on a graph (plural: axes)."},
    ],
    "position": [
        {"term": "coordinates", "definition": "A pair of numbers giving the exact position of a point on a grid — e.g. (3, 4)."},
        {"term": "x-axis", "definition": "The horizontal line on a coordinate grid."},
        {"term": "y-axis", "definition": "The vertical line on a coordinate grid."},
        {"term": "translation", "definition": "Sliding a shape to a new position without rotating or flipping it."},
        {"term": "reflection", "definition": "Flipping a shape over a mirror line."},
    ],
    "converting": [
        {"term": "convert", "definition": "Change a measurement from one unit to another — e.g. 150 cm = 1.5 m."},
        {"term": "metric", "definition": "The modern measurement system using metres, kilograms, litres, etc."},
        {"term": "imperial", "definition": "An older system using miles, pounds, pints, etc."},
        {"term": "equivalence", "definition": "When two measurements have the same value but use different units."},
        {"term": "proportion", "definition": "A way of comparing quantities — e.g. 1 kg ≈ 2.2 pounds."},
    ],
    "consolidation": [
        {"term": "review", "definition": "Look back over what you have learned to check and strengthen understanding."},
        {"term": "apply", "definition": "Use your knowledge in a new or different situation."},
        {"term": "reason", "definition": "Explain why an answer is correct using mathematical language."},
        {"term": "problem solving", "definition": "Working through a challenge by choosing and using the right maths skills."},
        {"term": "strategy", "definition": "A planned method used to approach and solve a problem."},
    ],
}

_SYSTEM_PROMPT = """You are generating a weekly maths digest for parents at Beaumont Primary School in Croydon.

Your job is to translate curriculum learning into something a parent can read in 2 minutes and actually use.

Tone rules:
- Plain English at all times. No jargon.
- Warm, calm, and encouraging. Never condescending.
- Practical. Parents are busy. Keep activities household-realistic (no special resources needed).
- British English spelling throughout.

You will be given the year group, unit title, curriculum small steps, key vocabulary, and times table focus.

Return ONLY a valid JSON object with exactly these keys:
{
  "plain_english": "2-3 sentences explaining what the children are learning this week in everyday language",
  "in_school": "2-3 sentences describing concretely how this looks in their lessons (hands-on, visual, then written)",
  "home_activity": "A short, specific activity a parent can do at home with their child. Must use only household items. 3-5 sentences.",
  "dinner_table_questions": ["Question 1?", "Question 2?", "Question 3?"],
  "key_vocabulary": [
    {"term": "word", "definition": "plain-English explanation a parent can understand"},
    ...
  ],
  "example_questions": ["Question 1", "Question 2", "Question 3"],
  "times_table_tip": "One practical sentence about the times table focus this week."
}

Return exactly 3 dinner_table_questions, 3-5 key_vocabulary entries, and 3 example_questions.
Do not include any text outside the JSON object.
"""


def generate_weekly_digest(
    year_group: str,
    term: str,
    week_number: int,
    unit_title: str,
    curriculum_context: dict[str, Any],
) -> dict[str, Any]:
    """Call Claude API to generate a weekly digest. Returns a dict matching DigestCreate fields."""
    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic package not installed; returning placeholder digest")
        return _placeholder_digest(year_group, unit_title)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set; returning placeholder digest")
        return _placeholder_digest(year_group, unit_title)

    client = anthropic.Anthropic(api_key=api_key)

    steps_text = "\n".join(f"- {s}" for s in curriculum_context.get("small_steps", []))
    vocab_text = ", ".join(curriculum_context.get("vocabulary_terms", []))
    tt_text = curriculum_context.get("times_table_expectation", "")
    stages_text = "\n".join(f"- {s}" for s in curriculum_context.get("method_stages", []))

    user_message = f"""Year group: {year_group.replace("_", " ").title()}
Term: {term.title()} Term, Week {week_number}
Unit: {unit_title}

Curriculum small steps this week:
{steps_text or "General maths skills for this year group"}

Key vocabulary for this year group:
{vocab_text or "Standard year group vocabulary"}

Times table focus: {tt_text or "Regular practice"}

CPA learning stages in use:
{stages_text}

Generate the weekly parent digest now."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return data
    except Exception as exc:
        logger.error("AI generation failed: %s", exc)
        return _placeholder_digest(year_group, unit_title)


def _placeholder_digest(year_group: str, unit_title: str) -> dict[str, Any]:
    """Fallback digest used when the Claude API is unavailable."""
    yg = year_group.replace("_", " ").title()
    return {
        "plain_english": (
            f"This week in {yg} maths, your child is working on {unit_title}. "
            "They are building on what they already know and developing new skills "
            "through hands-on activities and careful practice."
        ),
        "in_school": (
            "In lessons, children start by using practical resources to explore the concept, "
            "then move to drawing pictures and diagrams, and finally work with numbers and written methods. "
            "This concrete-to-abstract approach helps ideas stick."
        ),
        "home_activity": (
            f"Spend 5 minutes exploring {unit_title.lower()} together. "
            "Use everyday objects around the house — toys, fruit, or coins work well. "
            "Ask your child to show you what they did in school today. "
            "There are no right or wrong answers — just curious conversations."
        ),
        "dinner_table_questions": [
            f"What did you find tricky about {unit_title.lower()} today?",
            "Can you show me on your fingers or with something on the table?",
            "What's one thing you learned today that surprised you?",
        ],
        "key_vocabulary": [
            {"term": unit_title, "definition": f"The main topic your child is studying this week in {yg} maths."},
            {"term": "estimate", "definition": "Make a sensible guess before working something out exactly."},
            {"term": "explain", "definition": "Use words to describe how you worked something out."},
        ],
        "example_questions": [
            f"Can you explain {unit_title.lower()} in your own words?",
            "What strategy did you use?",
            "How do you know your answer is correct?",
        ],
        "times_table_tip": (
            "Practise your times tables for 2 minutes today — "
            "try saying them out loud while doing something else, like tidying up."
        ),
    }
