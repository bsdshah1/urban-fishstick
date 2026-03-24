"""Curriculum linking layer.

This module builds and queries cross-document curriculum relationships used by
feature modules such as lesson planning and gap analysis.

Classes
-------
CurriculumNode      Immutable node loaded from normalized JSON datasets.
CurriculumLink      Directed, scored relationship between two nodes.
LinkPersistence     Save/load CurriculumLink collections to/from JSON.
CurriculumLinker    Build, index, and query curriculum links.
CurriculumQueryAdapter  Feature-oriented queries over a built CurriculumLinker.
"""

from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# --- Path constants (anchored to this file so they work from any CWD) ---

_CONTENT_ROOT = Path(__file__).resolve().parent.parent.parent / "content"
_LINKS_DIR = _CONTENT_ROOT / "normalized" / "links"
_LINKS_FILE = _LINKS_DIR / "curriculum_links.json"

logger = logging.getLogger(__name__)

# --- Scoring constants ---

# Minimum Jaccard token similarity to form overview→progression or
# progression→vocabulary links.  A lower threshold captures more tenuous
# topic overlaps; raise it to require stronger keyword agreement.
SEMANTIC_MIN_SCORE = 0.10

# Minimum Jaccard similarity for linking a calculation policy method to a
# curriculum block via keyword overlap (year/strand exact match bypasses this).
CALC_POLICY_MIN_SCORE = 0.24

# Times-table scoring: base score when table numbers overlap, plus a per-table
# bonus capped at TABLE_MATCH_MAX_BONUS so the combined score stays ≤ 1.0.
TABLE_MATCH_BASE_SCORE = 0.80
TABLE_MATCH_SCORE_PER_TABLE = 0.05
TABLE_MATCH_MAX_BONUS = 0.20

# Fallback scores used when no shared table numbers are found.
TABLE_SAME_YEAR_AND_STRAND_SCORE = 0.60
TABLE_SAME_YEAR_SCORE = 0.45


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CurriculumNode:
    """Normalized curriculum node."""

    id: str
    node_type: str
    text: str = ""
    year: str | None = None
    strand: str | None = None
    title: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CurriculumNode":
        for required in ("id", "node_type"):
            if required not in data:
                raise ValueError(
                    f"CurriculumNode mapping is missing required field '{required}'. "
                    f"Received keys: {sorted(data.keys())}"
                )
        return cls(
            id=str(data["id"]),
            node_type=str(data["node_type"]),
            text=str(data.get("text") or ""),
            year=_normalize_year(data.get("year")),
            strand=_normalize_token(data.get("strand")),
            title=data.get("title"),
            tags=tuple(_normalize_token(tag) for tag in (data.get("tags") or [])),
        )


@dataclass(frozen=True)
class CurriculumLink:
    """Directed relationship between curriculum nodes."""

    source_id: str
    target_id: str
    relation: str
    score: float
    rationale: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "score": round(self.score, 3),
            "rationale": self.rationale,
        }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


class LinkPersistence:
    """Handles saving and loading CurriculumLink collections to/from JSON.

    Separated from CurriculumLinker so that storage concerns (file paths,
    serialisation format) can change without touching linking logic.
    """

    def __init__(self, links_path: Path = _LINKS_FILE) -> None:
        self.links_path = links_path

    def save(self, links: list[CurriculumLink]) -> Path:
        self.links_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "links": [link.to_mapping() for link in links],
            "meta": {"version": 1, "count": len(links)},
        }
        self.links_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved %d curriculum links to %s", len(links), self.links_path)
        return self.links_path

    def load(self) -> list[CurriculumLink]:
        try:
            raw = self.links_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(
                "Links file not found at %s; returning empty list", self.links_path
            )
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Corrupt curriculum links file at {self.links_path}: {exc}"
            ) from exc

        links = [
            CurriculumLink(
                source_id=row["source_id"],
                target_id=row["target_id"],
                relation=row["relation"],
                score=float(row["score"]),
                rationale=row["rationale"],
            )
            for row in payload.get("links", [])
        ]
        logger.info("Loaded %d curriculum links from %s", len(links), self.links_path)
        return links


# ---------------------------------------------------------------------------
# Linker
# ---------------------------------------------------------------------------


class CurriculumLinker:
    """Build, index, and query curriculum relationships."""

    def __init__(self, links_path: Path = _LINKS_FILE) -> None:
        self._persistence = LinkPersistence(links_path)
        self.links: list[CurriculumLink] = []
        self._links_by_source: dict[str, list[CurriculumLink]] = defaultdict(list)
        self._links_by_relation: dict[str, list[CurriculumLink]] = defaultdict(list)

    # --- Building ---

    def build_links(self, nodes: list[CurriculumNode]) -> list[CurriculumLink]:
        nodes_by_type = _group_by_type(nodes)
        links: list[CurriculumLink] = []

        links.extend(
            _build_links(
                sources=nodes_by_type["overview_block"],
                targets=nodes_by_type["progression_statement"],
                relation="overview_to_progression",
                score_fn=_semantic_score_fn(SEMANTIC_MIN_SCORE),
            )
        )
        links.extend(
            _build_links(
                sources=nodes_by_type["progression_statement"],
                targets=nodes_by_type["vocabulary_expectation"],
                relation="progression_to_vocabulary",
                score_fn=_semantic_score_fn(SEMANTIC_MIN_SCORE),
            )
        )
        links.extend(
            _build_links(
                sources=nodes_by_type["calculation_policy_method"],
                targets=(
                    nodes_by_type["overview_block"]
                    + nodes_by_type["year_block"]
                    + nodes_by_type["strand_block"]
                ),
                relation="policy_method_to_block",
                score_fn=_calc_policy_score_fn(),
            )
        )
        links.extend(
            _build_links(
                sources=nodes_by_type["times_table_focus"],
                targets=nodes_by_type["multiplication_division_objective"],
                relation="times_table_to_objective",
                score_fn=_times_table_score_fn(),
            )
        )

        relation_counts: dict[str, int] = defaultdict(int)
        for link in links:
            relation_counts[link.relation] += 1
        for relation, count in sorted(relation_counts.items()):
            logger.debug("  Built %d '%s' links (before dedup)", count, relation)

        deduped = _dedupe_links(links)
        self._index_links(deduped)
        logger.info(
            "Built %d curriculum links (%d after deduplication)", len(links), len(deduped)
        )
        return deduped

    # --- Persistence (delegated to LinkPersistence) ---

    def save_links(self) -> Path:
        return self._persistence.save(self.links)

    def load_links(self) -> list[CurriculumLink]:
        links = self._persistence.load()
        self._index_links(links)
        return links

    # --- Querying ---

    def links_for_source(
        self, source_id: str, relation: str | None = None
    ) -> list[CurriculumLink]:
        links = self._links_by_source.get(source_id, [])
        if relation is None:
            return links
        return [link for link in links if link.relation == relation]

    def links_by_relation(self, relation: str) -> list[CurriculumLink]:
        return list(self._links_by_relation.get(relation, []))

    def linked_targets(self, source_id: str, relation: str | None = None) -> list[str]:
        return [link.target_id for link in self.links_for_source(source_id, relation=relation)]

    # --- Feature-oriented query helpers ---

    def lesson_planner_context(self, overview_block_id: str) -> dict[str, list[str]]:
        progression = self.linked_targets(
            overview_block_id, relation="overview_to_progression"
        )
        vocabulary: list[str] = []
        for statement_id in progression:
            vocabulary.extend(
                self.linked_targets(statement_id, relation="progression_to_vocabulary")
            )
        return {
            "progression_statement_ids": progression,
            "vocabulary_expectation_ids": sorted(set(vocabulary)),
        }

    def gap_analysis_dependencies(self, objective_id: str) -> dict[str, list[str]]:
        return {
            "times_table_focus_ids": [
                link.source_id
                for link in self.links_by_relation("times_table_to_objective")
                if link.target_id == objective_id
            ],
            "calculation_method_ids": [
                link.source_id
                for link in self.links_by_relation("policy_method_to_block")
                if link.target_id == objective_id
            ],
        }

    def _index_links(self, links: list[CurriculumLink]) -> None:
        self.links = links
        self._links_by_source = defaultdict(list)
        self._links_by_relation = defaultdict(list)
        for link in links:
            self._links_by_source[link.source_id].append(link)
            self._links_by_relation[link.relation].append(link)


# ---------------------------------------------------------------------------
# Feature query adapter
# ---------------------------------------------------------------------------


class CurriculumQueryAdapter:
    """Feature-oriented queries over a built CurriculumLinker.

    Use this adapter in feature modules rather than calling CurriculumLinker
    directly.  The adapter provides a stable, feature-facing interface that
    can be extended or swapped without changing the linker internals.
    """

    def __init__(self, linker: CurriculumLinker) -> None:
        self._linker = linker

    def lesson_planner_context(self, overview_block_id: str) -> dict[str, list[str]]:
        return self._linker.lesson_planner_context(overview_block_id)

    def gap_analysis_dependencies(self, objective_id: str) -> dict[str, list[str]]:
        return self._linker.gap_analysis_dependencies(objective_id)


# ---------------------------------------------------------------------------
# Convenience API
# ---------------------------------------------------------------------------


def build_and_persist_curriculum_links(raw_nodes: list[dict[str, Any]]) -> Path:
    """Convenience API used by normalization pipelines."""
    linker = CurriculumLinker()
    nodes = [CurriculumNode.from_mapping(raw) for raw in raw_nodes]
    linker.build_links(nodes)
    return linker.save_links()


# ---------------------------------------------------------------------------
# Score functions
# ---------------------------------------------------------------------------

# Type alias: a score function accepts (source, target) nodes and returns
# (score, rationale) if a link should be created, or None to skip.
_ScoreFn = Callable[[CurriculumNode, CurriculumNode], tuple[float, str] | None]


def _semantic_score_fn(min_score: float) -> _ScoreFn:
    """Jaccard keyword overlap score function."""
    def score_fn(source: CurriculumNode, target: CurriculumNode) -> tuple[float, str] | None:
        source_terms = _token_set(source)
        target_terms = _token_set(target)
        if not source_terms or not target_terms:
            return None
        score = _jaccard(source_terms, target_terms)
        return (score, "keyword_overlap") if score >= min_score else None
    return score_fn


def _calc_policy_score_fn() -> _ScoreFn:
    """Score function for calculation policy method → curriculum block links."""
    def score_fn(method: CurriculumNode, block: CurriculumNode) -> tuple[float, str] | None:
        if _same_year_or_strand(method, block):
            return (1.0, "year_or_strand_match")
        method_terms = _token_set(method)
        block_terms = _token_set(block)
        if not method_terms or not block_terms:
            return None
        score = _jaccard(method_terms, block_terms)
        return (score, "keyword_overlap") if score >= CALC_POLICY_MIN_SCORE else None
    return score_fn


def _times_table_score_fn() -> _ScoreFn:
    """Score function for times-table focus → multiplication objective links."""
    def score_fn(focus: CurriculumNode, objective: CurriculumNode) -> tuple[float, str] | None:
        table_numbers = _extract_table_numbers(focus)
        objective_numbers = _extract_table_numbers(objective)
        same_year = bool(focus.year and objective.year and focus.year == objective.year)
        same_strand = bool(
            focus.strand and objective.strand and focus.strand == objective.strand
        )
        matched_numbers = table_numbers.intersection(objective_numbers)

        if matched_numbers:
            bonus = min(TABLE_MATCH_MAX_BONUS, TABLE_MATCH_SCORE_PER_TABLE * len(matched_numbers))
            score = TABLE_MATCH_BASE_SCORE + bonus
            rationale = f"shared_tables:{','.join(map(str, sorted(matched_numbers)))}"
            return (score, rationale)
        if same_year and same_strand:
            return (TABLE_SAME_YEAR_AND_STRAND_SCORE, "same_year_and_strand")
        if same_year:
            return (TABLE_SAME_YEAR_SCORE, "same_year")
        return None
    return score_fn


# ---------------------------------------------------------------------------
# Core link builder
# ---------------------------------------------------------------------------


def _build_links(
    *,
    sources: list[CurriculumNode],
    targets: list[CurriculumNode],
    relation: str,
    score_fn: _ScoreFn,
) -> list[CurriculumLink]:
    """Build links between all source/target pairs where score_fn returns a result."""
    links: list[CurriculumLink] = []
    for source in sources:
        for target in targets:
            result = score_fn(source, target)
            if result is None:
                continue
            score, rationale = result
            links.append(
                CurriculumLink(
                    source_id=source.id,
                    target_id=target.id,
                    relation=relation,
                    score=score,
                    rationale=rationale,
                )
            )
    return links


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _group_by_type(nodes: list[CurriculumNode]) -> dict[str, list[CurriculumNode]]:
    grouped: dict[str, list[CurriculumNode]] = defaultdict(list)
    for node in nodes:
        grouped[node.node_type].append(node)
    return grouped


def _token_set(node: CurriculumNode) -> set[str]:
    terms = set(_tokenize(node.text))
    if node.title:
        terms.update(_tokenize(node.title))
    if node.strand:
        terms.add(node.strand)
    terms.update(tag for tag in node.tags if tag)
    if node.year:
        terms.add(node.year)
    return terms


def _tokenize(value: str) -> list[str]:
    tokens = [token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2]
    return [_normalize_lexeme(token) for token in tokens]


def _normalize_lexeme(token: str) -> str:
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _normalize_token(value: Any) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\s+", "_", str(value).strip().lower())
    return normalized or None


def _normalize_year(value: Any) -> str | None:
    if value is None:
        return None
    match = re.search(r"(eyfs|year\s*\d+|y\d+)", str(value).lower())
    if not match:
        return _normalize_token(value)
    token = match.group(1).replace(" ", "")
    if token.startswith("y") and token != "eyfs":
        token = f"year{token[1:]}"
    return token


def _same_year_or_strand(left: CurriculumNode, right: CurriculumNode) -> bool:
    if left.year and right.year and left.year == right.year:
        return True
    if left.strand and right.strand and left.strand == right.strand:
        return True
    return False


def _extract_table_numbers(node: CurriculumNode) -> set[int]:
    haystack = " ".join(part for part in [node.title, node.text] if part)
    return {int(match) for match in re.findall(r"\b([2-9]|10|11|12)\b", haystack)}


def _dedupe_links(links: list[CurriculumLink]) -> list[CurriculumLink]:
    selected: dict[tuple[str, str, str], CurriculumLink] = {}
    for link in sorted(links, key=lambda link: link.score, reverse=True):
        key = (link.source_id, link.target_id, link.relation)
        selected.setdefault(key, link)
    return list(selected.values())
