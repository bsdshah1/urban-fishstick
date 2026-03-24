"""AI digest generator using the Anthropic Claude API."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

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
