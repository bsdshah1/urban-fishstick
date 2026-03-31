"""Curriculum adapter: reads normalized JSON datasets into memory.

Implements the CurriculumDomainService protocol from app/domain/services.py
using the pre-built normalized JSON datasets in app/content/normalized/v1/.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_V1_DIR = Path(__file__).resolve().parent.parent / "app" / "content" / "normalized" / "v1"


def _load(filename: str) -> list[dict[str, Any]]:
    path = _V1_DIR / filename
    return json.loads(path.read_text(encoding="utf-8")).get("records", [])


@lru_cache(maxsize=1)
def _all_small_steps() -> list[dict]:
    return _load("small_step.json")


@lru_cache(maxsize=1)
def _all_vocabulary() -> list[dict]:
    return _load("vocabulary_entries.json")


@lru_cache(maxsize=1)
def _all_times_tables() -> list[dict]:
    return _load("times_table_expectations.json")


@lru_cache(maxsize=1)
def _all_method_stages() -> list[dict]:
    return _load("method_stage.json")


@lru_cache(maxsize=1)
def _all_blocks() -> list[dict]:
    return _load("block.json")


def _unit_slug(unit_title: str) -> str:
    """Convert a unit title to the slug format used in block_id, e.g. "Just like me!" → "just_like_me"."""
    return re.sub(r"[^a-z0-9]+", "_", unit_title.lower()).strip("_")


# Maps White Rose block topic keywords to Maths_Progression.md block_name categories
_TOPIC_TO_STEP_BLOCKS: dict[str, list[str]] = {
    "addition": ["mental calculation", "written methods", "number bonds"],
    "subtraction": ["mental calculation", "written methods", "number bonds"],
    "multiplication": ["mental calculation", "written methods", "problem solving"],
    "division": ["mental calculation", "written methods", "problem solving"],
    "place value": ["understanding place value", "reading and writing numbers",
                    "comparing numbers", "identifying, representing and estimating",
                    "counting"],
    "fractions": ["measuring and calculating", "problem solving"],
    "decimals": ["measuring and calculating", "problem solving"],
    "percentage": ["measuring and calculating", "problem solving"],
    "geometry": ["identifying shapes and their properties",
                 "comparing and classifying"],
    "shape": ["identifying shapes and their properties",
              "comparing and classifying"],
    "angles": ["comparing and classifying / angles",
               "identifying shapes and their properties"],
    "measurement": ["measuring and calculating", "telling the time", "converting",
                    "comparing and estimating"],
    "length": ["measuring and calculating", "comparing and estimating"],
    "mass": ["measuring and calculating", "comparing and estimating"],
    "capacity": ["measuring and calculating", "comparing and estimating"],
    "time": ["telling the time", "measuring and calculating"],
    "money": ["measuring and calculating", "problem solving"],
    "area": ["measuring and calculating"],
    "perimeter": ["measuring and calculating"],
    "volume": ["measuring and calculating"],
    "converting": ["converting", "measuring and calculating"],
    "statistics": ["problem solving", "measuring and calculating"],
    "position": ["position, direction and movement"],
    "direction": ["position, direction and movement"],
    "ratio": ["problem solving", "mental calculation"],
    "algebra": ["problem solving", "mental calculation"],
    "consolidation": ["problem solving", "estimating and checking answers"],
}


def get_small_steps(year_group: str, unit_title: str) -> list[str]:
    """Return step descriptions for the given year group and unit (fuzzy block name/id match)."""
    unit_lower = unit_title.lower()
    slug = _unit_slug(unit_title)

    results = [
        step["description"]
        for step in _all_small_steps()
        if step.get("year_group_id") == year_group
        and (
            # Slug match against block_id (handles spaces/apostrophes/punctuation)
            slug in step.get("block_id", "").lower()
            # Exact substring match against block_id or block_name
            or unit_lower in step.get("block_id", "").lower()
            or unit_lower in step.get("block_name", "").lower()
        )
    ]
    if not results:
        # Topic-to-step-block mapping for White Rose blocks vs national curriculum categories
        step_block_keywords: list[str] = []
        for topic_kw, step_block_names in _TOPIC_TO_STEP_BLOCKS.items():
            if topic_kw in unit_lower:
                step_block_keywords.extend(step_block_names)
        if step_block_keywords:
            results = [
                step["description"]
                for step in _all_small_steps()
                if step.get("year_group_id") == year_group
                and any(
                    sbk in step.get("block_name", "").lower()
                    for sbk in step_block_keywords
                )
            ]
    if not results:
        # Keyword fallback: individual words from unit_title against block_name
        keywords = [w for w in re.split(r"[^a-z]+", unit_lower) if len(w) > 3]
        results = [
            step["description"]
            for step in _all_small_steps()
            if step.get("year_group_id") == year_group
            and any(kw in step.get("block_name", "").lower() for kw in keywords)
        ]
    if not results:
        # Final fallback: all steps for the year group (up to 6)
        results = [
            step["description"]
            for step in _all_small_steps()
            if step.get("year_group_id") == year_group
        ][:6]
    return results[:8]


def get_vocabulary_terms(year_group: str) -> list[str]:
    """Return vocabulary term labels for the given year group."""
    terms: list[str] = []
    for entry in _all_vocabulary():
        if entry.get("year_group_id") == year_group:
            strand = entry.get("strand", "")
            vocab = entry.get("vocabulary_terms", [])
            if vocab:
                terms.extend(vocab)
            elif strand:
                terms.append(strand)
    return terms[:12]


def get_times_table_expectation(year_group: str) -> str:
    """Return the times-table expectation string for the given year group."""
    for row in _all_times_tables():
        if row.get("year_group_id") == year_group:
            return row.get("expectation", "")
    return ""


def get_method_stages(topic_keyword: str = "") -> list[str]:
    """Return CPA stage descriptions (optionally filtered by topic keyword)."""
    topic_lower = topic_keyword.lower()
    stages = _all_method_stages()
    if topic_lower:
        filtered = [
            s["description"]
            for s in stages
            if topic_lower in s.get("id", "").lower()
        ]
        if filtered:
            return filtered
    return [s["description"] for s in stages[:3]]


def get_curriculum_context(year_group: str, unit_title: str) -> dict:
    """Return a bundled curriculum context dict for AI generation."""
    return {
        "small_steps": get_small_steps(year_group, unit_title),
        "vocabulary_terms": get_vocabulary_terms(year_group),
        "times_table_expectation": get_times_table_expectation(year_group),
        "method_stages": get_method_stages(unit_title),
    }
