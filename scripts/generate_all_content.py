#!/usr/bin/env python3
"""Batch generate parent digest content for all year groups and curriculum blocks.

Usage:
    python scripts/generate_all_content.py

Reads all blocks from the normalised JSON, calls the AI generator for each, and
saves one JSON file per block under:
    app/content/generated/digests/<year_group_id>/<term_id>/<block_id>.json

Falls back to placeholder digests gracefully when ANTHROPIC_API_KEY is unset.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Allow imports from the project root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from services.ai_generator import generate_weekly_digest  # noqa: E402
from services.curriculum_adapter import get_curriculum_context  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_V1_DIR = _PROJECT_ROOT / "app" / "content" / "normalized" / "v1"
_OUTPUT_ROOT = _PROJECT_ROOT / "app" / "content" / "generated" / "digests"


def _load(filename: str) -> list[dict]:
    path = _V1_DIR / filename
    return json.loads(path.read_text(encoding="utf-8")).get("records", [])


def _term_label(term_id: str) -> str:
    """Convert e.g. 'year_1__autumn_term' → 'autumn'."""
    parts = term_id.split("__")
    return parts[-1].replace("_term", "").replace("_", " ") if parts else term_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate parent digest content for all blocks.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all files, overwriting any that already exist.",
    )
    args = parser.parse_args()

    blocks = _load("block.json")
    logger.info("Loaded %d blocks", len(blocks))

    generated = 0
    skipped = 0

    for block in blocks:
        block_id: str = block["id"]
        year_group_id: str = block["year_group_id"]
        term_id: str = block["term_id"]
        block_name: str = block["name"]

        term_label = _term_label(term_id)

        output_path = _OUTPUT_ROOT / year_group_id / term_id / f"{block_id}.json"

        if output_path.exists() and not args.force:
            logger.info("  SKIP  %s (already exists)", block_id)
            skipped += 1
            continue

        logger.info("  GEN   %s / %s / %s", year_group_id, term_label, block_name)

        curriculum_context = get_curriculum_context(year_group_id, block_name)
        content = generate_weekly_digest(
            year_group=year_group_id,
            term=term_label,
            week_number=1,
            unit_title=block_name,
            curriculum_context=curriculum_context,
        )

        record = {
            "year_group": year_group_id,
            "term": term_label,
            "term_id": term_id,
            "block_id": block_id,
            "block_name": block_name,
            "week_number": 1,
            "unit_title": block_name,
            "content": content,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        generated += 1

    total = generated + skipped
    logger.info(
        "Done. %d/%d generated, %d skipped (already existed).",
        generated,
        total,
        skipped,
    )


if __name__ == "__main__":
    main()
