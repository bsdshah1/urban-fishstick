#!/usr/bin/env python3
"""Normalize markdown sources after passing validation checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def normalize_markdown_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    normalized = "\n".join(line.rstrip() for line in original.splitlines()) + "\n"
    if normalized != original:
        path.write_text(normalized, encoding="utf-8")
        return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize markdown files, running content quality validation first."
        )
    )
    parser.add_argument("--source-dir", default="context_docs_md", type=Path)
    parser.add_argument("--report-dir", default="reports/content_quality", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    validation_cmd = [
        sys.executable,
        "scripts/validate_markdown_sources.py",
        "--source-dir",
        str(args.source_dir),
        "--report-dir",
        str(args.report_dir),
    ]

    result = subprocess.run(validation_cmd, check=False)
    if result.returncode != 0:
        print("Validation failed; skipping normalization.")
        return result.returncode

    changed_files = 0
    for path in sorted(args.source_dir.glob("*.md")):
        if normalize_markdown_file(path):
            changed_files += 1

    print(f"Normalization complete. Files changed: {changed_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
