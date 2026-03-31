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

def _pick_vocabulary(unit_title: str, year_group: str) -> list[dict]:
    """Return 4-5 vocabulary entries from _VOCAB_BANK matching the topic."""
    tl = unit_title.lower()
    # Combined topics first (more specific)
    if "addition" in tl and "subtraction" in tl:
        return _VOCAB_BANK["addition"][:2] + _VOCAB_BANK["subtraction"][:2] + _VOCAB_BANK["addition"][4:5]
    if "multiplication" in tl and "division" in tl:
        return _VOCAB_BANK["multiplication"][:2] + _VOCAB_BANK["division"][:2] + _VOCAB_BANK["multiplication"][4:5]
    if "fractions" in tl and ("decimals" in tl or "percentage" in tl):
        return _VOCAB_BANK["fractions"][:2] + _VOCAB_BANK["decimals"][:2] + _VOCAB_BANK["percentage"][:1]
    if "area" in tl and "perimeter" in tl:
        return _VOCAB_BANK["area"][:3] + _VOCAB_BANK["perimeter"][:2]
    if "area" in tl and "volume" in tl:
        return _VOCAB_BANK["area"][:2] + _VOCAB_BANK["volume"][:3]
    # Single-topic match (longest keyword wins)
    for key in sorted(_VOCAB_BANK, key=len, reverse=True):
        if key in tl:
            return _VOCAB_BANK[key][:5]
    # EYFS fallback
    if year_group == "eyfs":
        return [
            {"term": "more", "definition": "A larger amount — e.g. 5 is more than 3."},
            {"term": "fewer", "definition": "A smaller number of something — e.g. 2 is fewer than 5."},
            {"term": "count", "definition": "Say numbers in order to find out how many there are."},
            {"term": "sort", "definition": "Put objects into groups based on a shared property."},
            {"term": "compare", "definition": "Look at two things to see how they are the same or different."},
        ]
    return _VOCAB_BANK["consolidation"][:4]


def _times_table_tip(tt_expectation: str, year_group: str) -> str:
    """Return a year-group-appropriate times table tip."""
    if year_group == "eyfs":
        return (
            "At this stage children are not learning times tables formally. "
            "Instead they explore equal groups through play — sharing objects fairly "
            "or making equal piles — which builds the foundation for multiplication later on."
        )
    tte = tt_expectation.lower()
    if year_group == "year_1" or "2, 5 and 10" in tte:
        return (
            "Year 1 focuses on the 2, 5, and 10 times tables. Try counting in 2s "
            "together on the stairs, or in 10s while counting out coins. "
            "Even 2–3 minutes a day builds the familiarity that pays off in Year 2."
        )
    if year_group == "year_2" or ("3" in tte and "4" not in tte):
        return (
            "Year 2 children learn their 2, 5, 10, and 3 times tables. The 3 times "
            "table is the new one this year. Try chanting together: 3, 6, 9, 12, 15 … "
            "Clapping a beat as you say the numbers helps the rhythm stick."
        )
    if year_group == "year_3" or "3, 4, 8" in tte:
        return (
            "Year 3 focuses on the 3, 4, 8, and 6 times tables. Try one table a week — "
            "write it out, then see how fast your child can say it forwards and backwards. "
            "The 8 times table is double the 4 times table, which is a handy shortcut!"
        )
    if year_group == "year_4" or "7, 9, 11" in tte:
        return (
            "Year 4 children should know all their times tables to 12 × 12 by the end "
            "of the year — the national Multiplication Tables Check happens in Year 4. "
            "Daily 3-minute practice mixing tables in random order is the best preparation."
        )
    if year_group == "year_5":
        return (
            "By Year 5 children should know all their times tables with speed and confidence. "
            "Ask quick-fire questions at dinner — mixing tables so they recall facts "
            "rather than just reciting sequences. Can they answer in under 3 seconds?"
        )
    if year_group == "year_6":
        return (
            "Year 6 children use all their times tables to tackle complex problems including "
            "long multiplication, division, and fractions. Challenge them: 'What is 7 × 12?' "
            "or 'How many 8s in 72?' Rapid recall frees up thinking space for harder work."
        )
    if tt_expectation.strip():
        return (
            f"The times table focus for this year group is: {tt_expectation}. "
            "Regular short practice — even 2–3 minutes a day — makes a big difference. "
            "Try mixing up the order so your child is recalling facts, not just counting up."
        )
    return (
        "Regular times table practice — just 2–3 minutes a day — helps your child recall "
        "facts quickly, freeing up thinking space for more complex problems. "
        "Mix different tables in random order rather than always going in sequence."
    )


_STEP_NOISE = (
    "this markdown", "oaicite", "contains overviews",
    "take this time to play", ".pdf", "originally",
)


def _clean_steps(steps: list[str]) -> list[str]:
    return [s for s in steps if len(s) > 10 and not any(n in s.lower() for n in _STEP_NOISE)]


def _plain_english(unit_title: str, year_group: str, steps: list[str]) -> str:
    yg = year_group.replace("_", " ").title()
    clean = _clean_steps(steps)
    if year_group == "eyfs":
        if clean:
            joined = "; ".join(s.lower().rstrip(".") for s in clean[:3])
            return (
                f"This week in {yg}, your child is exploring {unit_title}. "
                f"They will focus on: {joined}. "
                "All of this happens through play, stories, and practical activities that "
                "build early mathematical curiosity and confidence."
            )
        return (
            f"This week in {yg}, your child is exploring {unit_title} through play, "
            "stories, and hands-on activities. This is a crucial stage for developing "
            "mathematical curiosity — every game, song, and conversation counts."
        )
    if clean:
        if len(clean) >= 3:
            step_text = (
                f"{clean[0].lower().rstrip('.')}; "
                f"{clean[1].lower().rstrip('.')}; "
                f"and {clean[2].lower().rstrip('.')}."
            )
        elif len(clean) == 2:
            step_text = f"{clean[0].lower().rstrip('.')} and {clean[1].lower().rstrip('.')}."
        else:
            step_text = clean[0].lower().rstrip('.') + "."
        return (
            f"This week in {yg} maths, your child is working on {unit_title}. "
            f"The learning focuses on: {step_text} "
            "These skills build directly on what they have already mastered and "
            "prepare them for the next steps in the programme of study."
        )
    return (
        f"This week in {yg} maths, your child is working on {unit_title}. "
        "They are deepening skills that connect to earlier learning and lay the "
        "groundwork for what comes next. Ask them to tell you one thing they "
        "learned today — it is the best way to start a maths conversation."
    )


def _in_school_text(unit_title: str, year_group: str) -> str:
    tl = unit_title.lower()
    if year_group == "eyfs":
        return (
            f"In sessions, children explore {unit_title} through play, stories, "
            "and practical activities using real objects. Their teacher guides them "
            "through careful conversation, helping them notice patterns and relationships "
            "without formal recording."
        )
    if any(k in tl for k in ("addition", "subtraction", "multiplication", "division", "calculation")):
        return (
            "In lessons, children start with concrete resources — base ten blocks, "
            "counters, or number lines — to model calculations physically. They then "
            "represent what they have done using drawings and diagrams before practising "
            "the formal written method independently. This concrete → pictorial → abstract "
            "approach helps the method become secure before moving on."
        )
    if any(k in tl for k in ("fraction", "decimal", "percentage", "ratio")):
        return (
            "Children begin by folding paper, using fraction bars, and drawing bar models "
            "to see the concept visually before working with numbers and symbols. "
            "Discussion in pairs and small groups helps them explain and justify their "
            "reasoning using precise mathematical vocabulary."
        )
    if any(k in tl for k in ("shape", "geometry", "angle", "position", "direction")):
        return (
            "Children handle, sort, and classify 2-D and 3-D shapes, drawing and describing "
            "their properties. They use protractors, mirrors, and squared paper to explore "
            "angles, symmetry, and position. Explaining what they notice in precise "
            "mathematical language is a key part of every lesson."
        )
    if any(k in tl for k in ("measure", "length", "mass", "capacity", "time", "money",
                              "area", "perimeter", "volume", "convert")):
        return (
            "Children use practical measuring equipment — rulers, scales, measuring "
            "cylinders, and clocks — to explore measurement in real contexts. They record "
            "findings using diagrams and number lines before progressing to written "
            "calculations. Problem-solving tasks show how these skills are used every day."
        )
    if "statistic" in tl or "data" in tl:
        return (
            "Children collect, organise, and interpret data using tallies, tables, and a "
            "variety of charts and graphs. They practise reading scales accurately, "
            "comparing data sets, and answering questions from the information they gather."
        )
    if "place value" in tl:
        return (
            "In lessons, children use base ten blocks, place value charts, and number "
            "lines to explore how numbers are built from hundreds, tens, and ones. "
            "They represent the same number in different ways before working abstractly. "
            "Understanding place value is the foundation for all other maths, so lessons "
            "move carefully and thoroughly."
        )
    if "algebra" in tl:
        return (
            "Children are introduced to using letters as symbols for unknown numbers. "
            "Balance puzzles and practical activities make the abstract ideas concrete "
            "before pupils move to formal algebraic working with equations and formulas."
        )
    return (
        f"In lessons, children use practical resources and visual representations to "
        f"explore {unit_title.lower()}. They work from hands-on activities through to "
        "diagrams and then written methods, with class discussion and partner work "
        "helping every child understand and apply what they have learned."
    )


def _home_activity(unit_title: str, year_group: str) -> str:
    tl = unit_title.lower()
    if year_group == "eyfs":
        return (
            f"Spend a few minutes exploring {unit_title.lower()} together at home. "
            "Use whatever is around — pasta shapes to sort, buttons to count, or water "
            "to pour into different containers. Ask your child to show you what they have "
            "been doing in school. There are no wrong answers — just curious conversations "
            "and playful exploration."
        )
    if "place value" in tl:
        return (
            "Take a pack of playing cards (remove picture cards). Draw three or four cards "
            "and make as many different numbers as you can with those digits. Which is the "
            "biggest? The smallest? Try rounding each number to the nearest 100. "
            "No special equipment — just cards and conversation."
        )
    if "addition" in tl or "subtraction" in tl:
        return (
            "Roll two dice twice and use the numbers to make two 2-digit (or 3-digit) numbers. "
            "Add them together, then find the difference. Keep a running total over five "
            "rounds — who gets the highest? No calculators — the working-out is the fun part."
        )
    if "multiplication" in tl or "division" in tl:
        return (
            "Quiz each other on the times tables your child is focusing on this week. "
            "You say a question, they answer, then swap. Try it as a speed challenge: "
            "how many can they answer correctly in one minute? Mix up the order so it "
            "does not become just a chant — recall is the goal."
        )
    if "fraction" in tl:
        return (
            "Take a piece of paper and fold it into equal parts — halves, then quarters, "
            "then eighths. Shade some sections and ask: 'What fraction is shaded? "
            "What fraction is not?' A pizza or sandwich works just as well. "
            "Keep it visual and practical."
        )
    if "decimal" in tl or "percentage" in tl:
        return (
            "Look at price labels in the kitchen — tins, packets, or bottles. Practise "
            "reading decimal amounts aloud and round prices to the nearest pound. "
            "Estimate the total cost of a few items — this puts decimals in a real, "
            "meaningful context."
        )
    if "ratio" in tl:
        return (
            "Make a simple recipe together — squash and water (1 part squash to 4 parts "
            "water), or a salt-dough mix. Talk through the ratio as you measure: "
            "'For every 1 cup of squash we need 4 cups of water. If we double the recipe, "
            "what changes?' Seeing ratio in action makes it memorable."
        )
    if "algebra" in tl:
        return (
            "Try balance puzzles together: '? + 5 = 12. What is ?'. Start easy and make "
            "it gradually trickier. You can also look for patterns in times tables — "
            "in the 4 times table, what happens to the ones digit each time? "
            "Noticing patterns is the heart of algebra thinking."
        )
    if any(k in tl for k in ("shape", "geometry", "angle")):
        return (
            "Go on a shape hunt around the house. How many rectangles can you spot? "
            "Any cylinders in the kitchen? Count vertices and edges on a cereal box or tin. "
            "For angles, look for right angles (corners of doors) and ask whether other "
            "angles are acute or obtuse."
        )
    if any(k in tl for k in ("length", "perimeter")):
        return (
            "Use a piece of string to measure things around the house — is the sofa "
            "longer or shorter than the table? Estimate in centimetres first, then measure "
            "to check. For perimeter, measure all four sides of a book or tile and add them up."
        )
    if "area" in tl:
        return (
            "Draw a 1 cm grid on paper and ask your child to draw rectangles with an area "
            "of exactly 12 squares — how many different ones can they find? Then measure a "
            "book cover by counting grid squares to estimate its area."
        )
    if "mass" in tl:
        return (
            "Collect kitchen items and estimate which is heavier before checking on a "
            "kitchen scale. Order them lightest to heaviest. For older children, find the "
            "combined mass of two items and work out the difference between them."
        )
    if "capacity" in tl or "volume" in tl:
        return (
            "At bathtime or washing up, experiment with filling containers of different "
            "sizes. Which holds more? For older children, use a measuring jug: pour "
            "300 ml then 150 ml. How much is in the jug altogether? How much if you pour "
            "200 ml away?"
        )
    if "time" in tl:
        return (
            "Talk through the family routine using time language: 'We leave at quarter to 9', "
            "'lunch is at half past 12'. Ask your child to read the time on an analogue clock "
            "whenever they pass one. Time simple activities — how long does it take to "
            "brush your teeth?"
        )
    if "money" in tl:
        return (
            "Give your child a small collection of coins and ask them to make different "
            "amounts — can they make 37p in two different ways? At the shops (or in a "
            "pretend shop at home), let them work out change from £1 or £2. "
            "Handling real money builds confidence quickly."
        )
    if "statistic" in tl or "data" in tl:
        return (
            "Create a simple survey together — ask family members their favourite fruit, "
            "colour, or TV show. Record answers as a tally chart, then draw a bar chart. "
            "Ask: 'Which was most popular? How many more people chose X than Y?' "
            "This is exactly what they are doing in class."
        )
    if "position" in tl or "direction" in tl or "convert" in tl:
        return (
            "Look for real-life examples around the house — a map showing distances, a "
            "measuring jug with ml and pints, a food label in grams and kg. Ask your child "
            "to read the measurements and convert between them. Road signs in miles are "
            "another good context."
        )
    return (
        f"Spend 5 minutes exploring {unit_title.lower()} together. Ask your child to "
        "explain what they have been learning in school — teaching someone else is one "
        "of the best ways to understand something deeply. Use everyday objects if that "
        "helps, and follow your child's lead."
    )


def _dinner_questions(unit_title: str, year_group: str, steps: list[str]) -> list[str]:
    """Return 3 dinner-table questions, using clean small steps where available."""
    clean = _clean_steps(steps)
    if year_group == "eyfs":
        return [
            f"Can you show me something at home that is about {unit_title.lower()}?",
            "What was your favourite thing you did in maths today?",
            "Can you teach me one thing you learned this week?",
        ]
    q1 = (
        f"Can you show me how to {clean[0].lower().rstrip('.')}?"
        if clean else f"What does {unit_title.lower()} mean in your own words?"
    )
    q2 = (
        f"Was it easy or tricky to {clean[1].lower().rstrip('.')}? Why?"
        if len(clean) >= 2 else f"What was the trickiest part of {unit_title.lower()} today?"
    )
    return [q1, q2, "How would you explain today's maths to someone who has never seen it before?"]


def _example_questions(unit_title: str, year_group: str) -> list[str]:
    """Return 3 age- and topic-appropriate example questions."""
    tl = unit_title.lower()
    yg = year_group.replace("year_", "")

    if year_group == "eyfs":
        if any(k in tl for k in ("1, 2, 3", "count", "alive", "building", "growing", "20")):
            return ["Can you count out 5 objects?", "Which group has more — 4 or 5?", "Show me one more than 3."]
        if "pattern" in tl or "find my" in tl:
            return ["Can you copy this pattern: red, blue, red, blue?", "What comes next?", "Can you make your own pattern?"]
        if any(k in tl for k in ("shape", "circle", "triangle")):
            return ["Can you find something shaped like a circle?", "How many sides does a triangle have?", "Can you sort these into flat and solid shapes?"]
        if any(k in tl for k in ("move", "position", "direction")):
            return ["Can you put the teddy on top of the box?", "Can you walk forwards 3 steps then backwards 2?", "Where is the ball — in front or behind the chair?"]
        return ["Can you count to 10 and back to 0?", "Show me something heavier than this book.", "Can you find two things that are the same shape?"]

    if yg == "1":
        if "place value" in tl:
            return ["What is the tens digit in 47?", "Write the number forty-three.", "Which is greater — 58 or 85?"]
        if "addition" in tl or "subtraction" in tl:
            return ["What is 8 + 5?", "I have 13 apples and eat 6. How many are left?", "Find the missing number: 6 + ? = 14"]
        if "multiplication" in tl or "division" in tl:
            return ["How many altogether in 3 groups of 2?", "Share 10 equally between 2. How many each?", "Count in 5s to 20."]
        if "shape" in tl or "geometry" in tl:
            return ["Name a 3-D shape with 6 faces.", "How many sides does a pentagon have?", "Draw a shape with 4 equal sides."]
        return ["Count on from 47 to 52.", "What number is 10 more than 35?", "Put these in order: 26, 62, 16, 61."]

    if yg == "2":
        if "place value" in tl:
            return ["What is the value of 7 in 73?", "Write 56 as tens and ones.", "Order: 84, 48, 80, 40."]
        if "addition" in tl or "subtraction" in tl:
            return ["Work out 67 + 28.", "Find 95 − 38.", "I have £1.20 and spend 47p. How much is left?"]
        if "multiplication" in tl or "division" in tl:
            return ["What is 5 × 4?", "Share 18 equally between 3. How many in each group?", "Complete: 3 × ? = 21"]
        if "fraction" in tl:
            return ["Shade ¼ of a shape split into 4 equal parts.", "What fraction of 12 is 3?", "Write two fractions equal to ½."]
        if "shape" in tl or "geometry" in tl:
            return ["Name a quadrilateral with all sides equal.", "Draw a shape with exactly 1 line of symmetry.", "How many right angles does a rectangle have?"]
        if "statistic" in tl or "data" in tl:
            return ["How do you record data using a tally chart?", "Read the bar chart — which category has the most?", "How many more chose cats than dogs?"]
        return ["What is 38 + 45?", "Round 67 to the nearest 10.", "Write three hundred and twelve in numerals."]

    if yg == "3":
        if "place value" in tl:
            return ["What is 100 more than 2,870?", "Round 3,468 to the nearest 100.", "Write 4,305 in words."]
        if "addition" in tl or "subtraction" in tl:
            return ["Work out 456 + 278 using column addition.", "Calculate 703 − 348.", "What is the difference between 650 and 423?"]
        if "multiplication" in tl or "division" in tl:
            return ["Work out 34 × 3.", "48 ÷ 4 = ?", "56 children in 8 equal groups. How many in each?"]
        if "fraction" in tl:
            return ["Which is greater — ⅔ or ¾?", "What is ½ of 48?", "Write ⅗ as a diagram."]
        if "length" in tl or "perimeter" in tl:
            return ["Find the perimeter of a rectangle 7 cm × 4 cm.", "Convert 250 cm into metres and centimetres.", "Which is longer — 2.5 m or 280 cm?"]
        if "time" in tl:
            return ["A film starts at 2:45 pm and lasts 1 hour 20 min. When does it end?", "How many minutes in 2½ hours?", "Write 09:30 in 12-hour time."]
        if "mass" in tl or "capacity" in tl:
            return ["Order: 1.2 kg, 850 g, 1,100 g.", "Convert 2.5 litres to millilitres.", "Which is heavier — 3.4 kg or 3,450 g?"]
        if "fraction" in tl:
            return ["Shade ¾ of a shape.", "Write an equivalent fraction for ½.", "Order ¼, ½, ¾ from smallest to largest."]
        if "money" in tl:
            return ["What is the change from £5.00 if you spend £3.47?", "Write £4.06 in words.", "Add £2.35 and £1.79."]
        if "shape" in tl or "geometry" in tl:
            return ["Name an angle less than 90°.", "Draw a shape with exactly 1 pair of parallel sides.", "How many right angles in a rectangle?"]
        if "statistic" in tl:
            return ["Read the bar chart — how many more chose option A than B?", "Draw a pictogram where each symbol = 2 people.", "What is the total frequency?"]
        return ["Work out 238 × 4.", "What is ⅔ of 24?", "Find the perimeter of a square with side 6 cm."]

    if yg == "4":
        if "place value" in tl:
            return ["Write 45,302 in words.", "What is the value of 8 in 38,450?", "Round 67,840 to the nearest 1,000."]
        if "multiplication" in tl or "division" in tl:
            return ["Work out 46 × 23.", "Calculate 196 ÷ 7.", "A box holds 24 crayons. How many in 15 boxes?"]
        if "fraction" in tl or "decimal" in tl:
            return ["Convert ⅗ to a decimal.", "Order: 0.4, 0.04, 0.44.", "What is ¾ of 60?"]
        if "area" in tl or "perimeter" in tl:
            return ["Find the area of a rectangle 8 cm × 6 cm.", "Find the perimeter of a square with side 9 cm.", "A rectangle has perimeter 28 cm and width 5 cm. Find its length."]
        if "time" in tl:
            return ["A train leaves at 11:48 and arrives at 13:07. How long is the journey?", "Convert 3.5 hours to hours and minutes.", "What time is 2 h 45 min before midnight?"]
        if "shape" in tl or "geometry" in tl:
            return ["Plot the point (3, 5) on a coordinate grid.", "Translate the shape 2 right and 3 up.", "Name a quadrilateral with exactly one pair of parallel sides."]
        if "statistic" in tl:
            return ["Read the line graph — what happened between 10 am and 12 noon?", "Draw a bar chart for: red 8, blue 5, green 11.", "What was the modal colour?"]
        return ["Work out 345 × 12.", "Convert 3.7 km to metres.", "Find a common factor of 24 and 36."]

    if yg == "5":
        if "place value" in tl:
            return ["Write 2,045,307 in words.", "Round 4,378,201 to the nearest million.", "What is the value of 3 in 7,300,000?"]
        if "fraction" in tl or "decimal" in tl or "percentage" in tl:
            return ["Convert 0.35 to a fraction in its simplest form.", "Find 15% of 240.", "Write ⅜ as a decimal and as a percentage."]
        if "multiplication" in tl or "division" in tl:
            return ["Work out 324 × 46.", "Calculate 1,248 ÷ 16.", "Find all factor pairs of 36."]
        if "area" in tl or "perimeter" in tl or "volume" in tl:
            return ["Find the area of a triangle with base 8 cm and height 5 cm.", "A cuboid is 4 cm × 3 cm × 5 cm. Find its volume.", "Find the perimeter of the compound shape."]
        if "statistic" in tl:
            return ["Find the mean of: 4, 7, 9, 6, 4.", "Describe the trend shown in the line graph.", "In a survey of 60 people, 25% chose red. How many is that?"]
        if "shape" in tl or "geometry" in tl or "angle" in tl:
            return ["Find the missing angle in the triangle (angles: 65°, 48°, ?).", "Name a quadrilateral with diagonals that bisect at right angles.", "Measure this angle with a protractor."]
        if "convert" in tl:
            return ["Convert 2.4 kg to grams.", "How many cm in 3.5 m?", "A recipe uses 750 ml. How many litres is that?"]
        return ["Work out 472 × 35.", "Write 0.375 as a fraction in its simplest form.", "Find 30% of 840."]

    if yg == "6":
        if "ratio" in tl:
            return ["Write 15:25 in its simplest form.", "Divide £72 in the ratio 3:5.", "A recipe uses flour and butter in ratio 4:1. If you use 200 g flour, how much butter?"]
        if "algebra" in tl:
            return ["Solve: 3n + 5 = 20.", "Find the value of 2a + b when a = 4 and b = 3.", "Write the first five terms of the sequence with rule 2n + 1."]
        if "fraction" in tl or "decimal" in tl or "percentage" in tl:
            return ["Calculate ³⁄₇ of 84.", "Increase 450 by 12%.", "Write 0.245 as a fraction in its simplest form."]
        if "area" in tl or "volume" in tl or "perimeter" in tl:
            return ["Find the area of a parallelogram with base 10 cm and height 6 cm.", "A cuboid is 5 cm × 4 cm × 3 cm. Find its volume.", "Find the area of a trapezium with parallel sides 8 cm and 5 cm, height 4 cm."]
        if "statistic" in tl:
            return ["Find the mean, median, and range of: 5, 8, 3, 9, 5.", "A pie chart shows 25% red. What angle does that sector have?", "A survey of 120 people found 35% preferred cinema. How many is that?"]
        if "place value" in tl:
            return ["Write 4,098,302 in words.", "Arrange in order: −5, −1, 0, −3, 2.", "Round 4.3578 to two decimal places."]
        if "shape" in tl or "geometry" in tl:
            return ["Find the sum of interior angles in a pentagon.", "Reflect the shape in the y-axis.", "Name the 3-D shape with 2 circular faces."]
        if "convert" in tl:
            return ["Convert 3.4 km to metres.", "Change 2.6 kg to grams.", "How many ml in 1.75 litres?"]
        return ["Work out 846 × 73.", "Solve: 4n − 7 = 21.", "Find 65% of 320."]

    return [
        f"Can you explain {unit_title.lower()} in your own words?",
        "Show me one example using numbers you choose yourself.",
        "How do you know your answer is correct?",
    ]


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
