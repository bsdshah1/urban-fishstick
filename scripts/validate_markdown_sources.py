#!/usr/bin/env python3
"""Validate markdown source quality before normalization."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOP_LEVEL_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")
DANGLING_CITATION_RE = re.compile(r":contentReference\[[^\]]*\](?:\{[^\}]*\})?")
FENCE_RE = re.compile(r"^(```|~~~)")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


@dataclass(frozen=True)
class Issue:
    check: str
    file: str
    line: int
    details: str


@dataclass(frozen=True)
class ValidationResult:
    file: str
    issues: list[Issue]


def iter_markdown_files(source_dir: Path) -> Iterable[Path]:
    return sorted(path for path in source_dir.glob("*.md") if path.is_file())


def detect_duplicate_top_level_headings(lines: list[str], file: str) -> list[Issue]:
    issues: list[Issue] = []
    seen: dict[str, int] = {}

    for idx, line in enumerate(lines, start=1):
        match = TOP_LEVEL_HEADING_RE.match(line)
        if not match:
            continue

        title = match.group(1).strip()
        key = re.sub(r"\s+", " ", title).casefold()
        if key in seen:
            issues.append(
                Issue(
                    check="duplicate_top_level_heading",
                    file=file,
                    line=idx,
                    details=f"Duplicate heading '{title}' (first seen on line {seen[key]}).",
                )
            )
        else:
            seen[key] = idx

    return issues


def detect_dangling_citation_artifacts(lines: list[str], file: str) -> list[Issue]:
    issues: list[Issue] = []
    for idx, line in enumerate(lines, start=1):
        if DANGLING_CITATION_RE.search(line):
            issues.append(
                Issue(
                    check="dangling_citation_artifact",
                    file=file,
                    line=idx,
                    details="Found unresolved contentReference citation artifact.",
                )
            )
    return issues


def detect_truncated_code_fences(lines: list[str], file: str) -> list[Issue]:
    issues: list[Issue] = []
    fence_stack: list[tuple[str, int]] = []

    for idx, line in enumerate(lines, start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue

        token = match.group(1)
        if fence_stack and fence_stack[-1][0] == token:
            fence_stack.pop()
        else:
            fence_stack.append((token, idx))

    for token, start_line in fence_stack:
        issues.append(
            Issue(
                check="truncated_code_fence",
                file=file,
                line=start_line,
                details=f"Unclosed code fence starting with '{token}'.",
            )
        )

    return issues


def detect_truncated_tables(lines: list[str], file: str) -> list[Issue]:
    issues: list[Issue] = []
    idx = 0

    while idx < len(lines):
        if "|" not in lines[idx]:
            idx += 1
            continue

        start = idx
        while idx < len(lines) and "|" in lines[idx] and lines[idx].strip():
            idx += 1

        block = lines[start:idx]
        if len(block) >= 2 and not any(TABLE_SEPARATOR_RE.match(row) for row in block[1:]):
            issues.append(
                Issue(
                    check="truncated_table",
                    file=file,
                    line=start + 1,
                    details="Table-like block is missing a valid header separator row.",
                )
            )

    return issues


def detect_unexpected_empty_sections(lines: list[str], file: str) -> list[Issue]:
    issues: list[Issue] = []
    headings: list[tuple[int, int, str]] = []

    for idx, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            headings.append((idx, level, match.group(2).strip()))

    for i, (line_no, level, title) in enumerate(headings):
        end = len(lines)
        for next_line, next_level, _ in headings[i + 1 :]:
            if next_level <= level:
                end = next_line - 1
                break

        section_lines = lines[line_no:end]
        meaningful = [
            line
            for line in section_lines
            if line.strip() and not line.strip().startswith("<!--")
        ]

        if not meaningful:
            issues.append(
                Issue(
                    check="unexpected_empty_section",
                    file=file,
                    line=line_no,
                    details=f"Section '{title}' has no body content.",
                )
            )

    return issues


def validate_markdown_file(path: Path) -> ValidationResult:
    lines = path.read_text(encoding="utf-8").splitlines()
    file = str(path)

    issues = []
    issues.extend(detect_duplicate_top_level_headings(lines, file))
    issues.extend(detect_dangling_citation_artifacts(lines, file))
    issues.extend(detect_truncated_code_fences(lines, file))
    issues.extend(detect_truncated_tables(lines, file))
    issues.extend(detect_unexpected_empty_sections(lines, file))

    return ValidationResult(file=file, issues=issues)


def write_reports(results: list[ValidationResult], report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = report_dir / f"validation_{timestamp}.json"
    latest_path = report_dir / "latest.json"

    payload = {
        "timestamp_utc": timestamp,
        "summary": {
            "files_checked": len(results),
            "files_with_issues": sum(1 for result in results if result.issues),
            "total_issues": sum(len(result.issues) for result in results),
        },
        "results": [
            {
                "file": result.file,
                "issues": [issue.__dict__ for issue in result.issues],
            }
            for result in results
        ],
    }

    text = json.dumps(payload, indent=2)
    json_path.write_text(text + "\n", encoding="utf-8")
    latest_path.write_text(text + "\n", encoding="utf-8")
    return json_path, latest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate markdown sources and emit a content quality report."
    )
    parser.add_argument(
        "--source-dir",
        default="context_docs_md",
        type=Path,
        help="Directory containing markdown sources.",
    )
    parser.add_argument(
        "--report-dir",
        default="reports/content_quality",
        type=Path,
        help="Directory to write validation reports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    markdown_files = list(iter_markdown_files(args.source_dir))
    if not markdown_files:
        print(f"No markdown files found in {args.source_dir}")
        return 0

    results = [validate_markdown_file(path) for path in markdown_files]
    report_path, latest_path = write_reports(results, args.report_dir)

    total_issues = sum(len(result.issues) for result in results)
    print(f"Validated {len(markdown_files)} files.")
    print(f"Total issues: {total_issues}")
    print(f"Report: {report_path}")
    print(f"Latest report alias: {latest_path}")

    return 1 if total_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
