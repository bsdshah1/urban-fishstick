#!/usr/bin/env python3
"""Normalize curriculum markdown extracts into versioned JSON datasets."""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

VERSION = "v1"

# Anchor default paths to the project root so the script works from any CWD.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

SOURCE_QUALITY_BY_FILE = {
    "Maths_Overview.md": "full_text",
    "Maths_Progression.md": "partial_extract",
    "Maths_Vocabulary_Progression.md": "summary_from_visual",
    "Times_Table_Progression.md": "full_text",
    "Addition_and_Subtraction_Calculation_Policy.md": "summary_from_visual",
    "Multiplication_and_Division_Calculation_Policy.md": "summary_from_visual",
    "EYFS_Calculation_Policy.md": "summary_from_visual",
}


def slugify(text: str) -> str:
    value = text.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def make_metadata(source_file: str) -> dict[str, str]:
    return {
        "source_file": source_file,
        "source_quality": SOURCE_QUALITY_BY_FILE.get(source_file, "partial_extract"),
    }


def parse_overview(content: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    year_groups: OrderedDict[str, dict[str, Any]] = OrderedDict()
    terms: list[dict[str, Any]] = []
    strands: OrderedDict[str, dict[str, Any]] = OrderedDict()
    blocks: list[dict[str, Any]] = []
    small_steps: list[dict[str, Any]] = []

    lines = content.splitlines()
    current_year = None
    current_term = None
    current_block = None
    md = make_metadata("Maths_Overview.md")

    for raw in lines:
        line = raw.strip()

        year_match = re.match(r"^##\s+(EYFS|Year\s+\d+)\s+Overview", line)
        if year_match:
            current_year = year_match.group(1)
            year_id = slugify(current_year)
            year_groups.setdefault(
                year_id,
                {
                    "id": year_id,
                    "name": current_year,
                    "key_stage": "EYFS" if current_year == "EYFS" else "KS1" if current_year in {"Year 1", "Year 2"} else "KS2",
                    "metadata": md,
                },
            )
            current_term = None
            current_block = None
            continue

        term_match = re.match(r"^###\s+(Autumn|Spring|Summer)\s+Term$", line)
        if term_match and current_year:
            term_name = f"{term_match.group(1)} Term"
            term_id = f"{slugify(current_year)}__{slugify(term_name)}"
            terms.append(
                {
                    "id": term_id,
                    "year_group_id": slugify(current_year),
                    "name": term_name,
                    "metadata": md,
                }
            )
            current_term = term_id
            current_block = None
            continue

        block_match = re.match(r"^-\s+\*\*(.+?)\*\*\s*(.*)", line)
        if block_match and current_term and current_year:
            block_label = block_match.group(1).strip()
            remainder = block_match.group(2).strip()
            strand_name = "Integrated"
            name = block_label

            if block_label.endswith(":"):
                # Format: **Strand:** Block name *(qualifier)*
                strand_name = block_label[:-1].strip()
                name = remainder
            elif ":" in block_label:
                left, right = block_label.split(":", 1)
                strand_name = left.strip()
                name = right.strip() or remainder

            # Convert italic qualifiers like *(within 10)* → (within 10)
            # Keep the qualifier text so block names remain unique; just remove the * markers.
            name = re.sub(r"\*\(([^)]+)\)\*", r"(\1)", name).strip()

            strand_id = slugify(strand_name)
            strands.setdefault(
                strand_id,
                {"id": strand_id, "name": strand_name, "metadata": md},
            )

            block_id = f"{current_term}__{slugify(name)}"
            blocks.append(
                {
                    "id": block_id,
                    "year_group_id": slugify(current_year),
                    "term_id": current_term,
                    "strand_id": strand_id,
                    "name": name,
                    "metadata": md,
                }
            )
            current_block = block_id
            continue

        substep_match = re.match(r"^-\s+(.+)$", line)
        if substep_match and current_block and current_year and not line.startswith("- **"):
            text = substep_match.group(1).strip()
            step_id = f"{current_block}__{slugify(text)[:48]}"
            small_steps.append(
                {
                    "id": step_id,
                    "year_group_id": slugify(current_year),
                    "block_id": current_block,
                    "description": text,
                    "metadata": md,
                }
            )

    return list(year_groups.values()), terms, list(strands.values()), blocks, small_steps


def parse_progression(content: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    strands: OrderedDict[str, dict[str, Any]] = OrderedDict()
    small_steps: list[dict[str, Any]] = []

    current_strand = None
    current_block = None
    current_year = None
    md = make_metadata("Maths_Progression.md")

    for raw in content.splitlines():
        line = raw.strip()

        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            if title.lower().startswith("progression map"):
                continue
            current_strand = title
            strand_id = slugify(current_strand)
            strands.setdefault(strand_id, {"id": strand_id, "name": current_strand, "metadata": md})
            continue

        if line.startswith("## "):
            current_block = line[3:].strip()
            continue

        year_match = re.match(r"^###\s+(EYFS|Year\s+\d+)$", line)
        if year_match:
            current_year = year_match.group(1)
            continue

        bullet_match = re.match(r"^-\s+(.+)$", line)
        if bullet_match and current_year and current_block and current_strand:
            text = bullet_match.group(1).strip()
            step_id = f"{slugify(current_year)}__{slugify(current_strand)}__{slugify(current_block)}__{slugify(text)[:32]}"
            small_steps.append(
                {
                    "id": step_id,
                    "year_group_id": slugify(current_year),
                    "strand_id": slugify(current_strand),
                    "block_name": current_block,
                    "description": text,
                    "metadata": md,
                }
            )

    return list(strands.values()), small_steps


def parse_method_stages(content: str, source_file: str) -> list[dict[str, Any]]:
    stages = []
    md = make_metadata(source_file)

    definitions = {
        "concrete": "Children use physical objects and manipulatives.",
        "pictorial": "Children use drawings and visual representations.",
        "abstract": "Children use numerals and formal written methods.",
    }

    for name, desc in definitions.items():
        if name.capitalize() in content or name in content.lower():
            stages.append(
                {
                    "id": f"{slugify(source_file.replace('.md', ''))}__{name}",
                    "stage": name,
                    "description": desc,
                    "metadata": md,
                }
            )

    return stages


def parse_vocabulary(content: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    md = make_metadata("Maths_Vocabulary_Progression.md")

    current_year = None
    in_typical = False
    for raw in content.splitlines():
        line = raw.strip()

        year_match = re.match(r"^###\s+(EYFS|Year\s+\d+)$", line)
        if year_match:
            current_year = year_match.group(1)
            in_typical = False
            continue

        if line.startswith("**Typical strands include"):
            in_typical = True
            continue

        if in_typical and line.startswith("- ") and current_year:
            strand = line.removeprefix("- ").strip()
            entry_id = f"{slugify(current_year)}__{slugify(strand)}"
            entries.append(
                {
                    "id": entry_id,
                    "year_group_id": slugify(current_year),
                    "strand": strand,
                    "vocabulary_terms": [],
                    "metadata": md,
                }
            )
        elif in_typical and not line:
            in_typical = False

    return entries


def parse_times_tables(content: str) -> list[dict[str, Any]]:
    rows = []
    md = make_metadata("Times_Table_Progression.md")

    for raw in content.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if "Year Group" in line or "---" in line:
            continue

        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) != 2:
            logging.warning("Skipping malformed times-table row (expected 2 columns): %r", line)
            continue

        year, focus = parts
        rows.append(
            {
                "id": f"{slugify(year)}__times_tables",
                "year_group_id": slugify(year),
                "expectation": focus,
                "metadata": md,
            }
        )

    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=_PROJECT_ROOT / "context_docs_md", type=Path)
    parser.add_argument("--output-dir", default=_PROJECT_ROOT / "app/content/normalized", type=Path)
    args = parser.parse_args()

    source_dir: Path = args.input_dir
    output_root: Path = args.output_dir
    version_dir = output_root / VERSION

    overview_text = load_text(source_dir / "Maths_Overview.md")
    progression_text = load_text(source_dir / "Maths_Progression.md")
    vocab_text = load_text(source_dir / "Maths_Vocabulary_Progression.md")
    tts_text = load_text(source_dir / "Times_Table_Progression.md")
    add_sub_text = load_text(source_dir / "Addition_and_Subtraction_Calculation_Policy.md")
    mul_div_text = load_text(source_dir / "Multiplication_and_Division_Calculation_Policy.md")
    eyfs_calc_text = load_text(source_dir / "EYFS_Calculation_Policy.md")

    year_groups, terms, overview_strands, blocks, overview_steps = parse_overview(overview_text)
    progression_strands, progression_steps = parse_progression(progression_text)

    strand_map: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for record in [*overview_strands, *progression_strands]:
        strand_map.setdefault(record["id"], record)

    small_steps = [*overview_steps, *progression_steps]
    method_stages = [
        *parse_method_stages(add_sub_text, "Addition_and_Subtraction_Calculation_Policy.md"),
        *parse_method_stages(mul_div_text, "Multiplication_and_Division_Calculation_Policy.md"),
        *parse_method_stages(eyfs_calc_text, "EYFS_Calculation_Policy.md"),
    ]

    datasets = {
        "year_group": year_groups,
        "term": terms,
        "strand": list(strand_map.values()),
        "block": blocks,
        "small_step": small_steps,
        "method_stage": method_stages,
        "vocabulary_entries": parse_vocabulary(vocab_text),
        "times_table_expectations": parse_times_tables(tts_text),
    }

    write_json(
        output_root / "manifest.json",
        {
            "version": VERSION,
            "input_dir": str(source_dir),
            "datasets": sorted(datasets.keys()),
            "source_quality_levels": ["full_text", "summary_from_visual", "partial_extract"],
        },
    )

    for name, records in datasets.items():
        write_json(version_dir / f"{name}.json", {"version": VERSION, "records": records})
        logging.info("  %-30s %d records", name, len(records))

    logging.info("Normalization complete. Output: %s", version_dir)


if __name__ == "__main__":
    main()
