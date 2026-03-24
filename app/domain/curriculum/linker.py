"""Curriculum linking layer.

This module builds and queries cross-document curriculum relationships used by
feature modules such as lesson planning and gap analysis.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
import json
import re
from typing import Any

LINKS_DIR = Path("app/content/normalized/links")
LINKS_FILE = LINKS_DIR / "curriculum_links.json"


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


class CurriculumLinker:
    """Build, persist, and query curriculum relationships."""

    def __init__(self, links_path: Path = LINKS_FILE) -> None:
        self.links_path = links_path
        self.links: list[CurriculumLink] = []
        self._links_by_source: dict[str, list[CurriculumLink]] = defaultdict(list)
        self._links_by_relation: dict[str, list[CurriculumLink]] = defaultdict(list)

    def build_links(self, nodes: list[CurriculumNode]) -> list[CurriculumLink]:
        nodes_by_type = _group_by_type(nodes)
        links: list[CurriculumLink] = []

        links.extend(
            self._link_by_semantic_overlap(
                sources=nodes_by_type["overview_block"],
                targets=nodes_by_type["progression_statement"],
                relation="overview_to_progression",
                min_score=0.10,
            )
        )
        links.extend(
            self._link_by_semantic_overlap(
                sources=nodes_by_type["progression_statement"],
                targets=nodes_by_type["vocabulary_expectation"],
                relation="progression_to_vocabulary",
                min_score=0.10,
            )
        )
        links.extend(
            self._link_calc_policy_to_year_strand(
                policy_methods=nodes_by_type["calculation_policy_method"],
                year_or_strand_blocks=(
                    nodes_by_type["overview_block"]
                    + nodes_by_type["year_block"]
                    + nodes_by_type["strand_block"]
                ),
            )
        )
        links.extend(
            self._link_times_tables_to_objectives(
                times_table_focuses=nodes_by_type["times_table_focus"],
                objectives=nodes_by_type["multiplication_division_objective"],
            )
        )

        deduped = _dedupe_links(links)
        self._index_links(deduped)
        return deduped

    def save_links(self) -> Path:
        LINKS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "links": [link.to_mapping() for link in self.links],
            "meta": {
                "version": 1,
                "count": len(self.links),
            },
        }
        self.links_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.links_path

    def load_links(self) -> list[CurriculumLink]:
        payload = json.loads(self.links_path.read_text(encoding="utf-8"))
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
        self._index_links(links)
        return links

    def links_for_source(self, source_id: str, relation: str | None = None) -> list[CurriculumLink]:
        links = self._links_by_source.get(source_id, [])
        if relation is None:
            return links
        return [link for link in links if link.relation == relation]

    def links_by_relation(self, relation: str) -> list[CurriculumLink]:
        return list(self._links_by_relation.get(relation, []))

    def linked_targets(self, source_id: str, relation: str | None = None) -> list[str]:
        return [link.target_id for link in self.links_for_source(source_id, relation=relation)]

    # Feature-oriented query helpers
    def lesson_planner_context(self, overview_block_id: str) -> dict[str, list[str]]:
        progression = self.linked_targets(
            overview_block_id,
            relation="overview_to_progression",
        )
        vocabulary: list[str] = []
        for statement_id in progression:
            vocabulary.extend(
                self.linked_targets(
                    statement_id,
                    relation="progression_to_vocabulary",
                )
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

    def _link_by_semantic_overlap(
        self,
        *,
        sources: list[CurriculumNode],
        targets: list[CurriculumNode],
        relation: str,
        min_score: float,
    ) -> list[CurriculumLink]:
        links: list[CurriculumLink] = []
        for source in sources:
            source_terms = _token_set(source)
            if not source_terms:
                continue
            for target in targets:
                target_terms = _token_set(target)
                if not target_terms:
                    continue
                score = _jaccard(source_terms, target_terms)
                if score < min_score:
                    continue
                links.append(
                    CurriculumLink(
                        source_id=source.id,
                        target_id=target.id,
                        relation=relation,
                        score=score,
                        rationale="keyword_overlap",
                    )
                )
        return links

    def _link_calc_policy_to_year_strand(
        self,
        *,
        policy_methods: list[CurriculumNode],
        year_or_strand_blocks: list[CurriculumNode],
    ) -> list[CurriculumLink]:
        links: list[CurriculumLink] = []
        for method in policy_methods:
            method_terms = _token_set(method)
            for block in year_or_strand_blocks:
                if _same_year_or_strand(method, block):
                    links.append(
                        CurriculumLink(
                            source_id=method.id,
                            target_id=block.id,
                            relation="policy_method_to_block",
                            score=1.0,
                            rationale="year_or_strand_match",
                        )
                    )
                    continue

                block_terms = _token_set(block)
                if not method_terms or not block_terms:
                    continue
                score = _jaccard(method_terms, block_terms)
                if score >= 0.24:
                    links.append(
                        CurriculumLink(
                            source_id=method.id,
                            target_id=block.id,
                            relation="policy_method_to_block",
                            score=score,
                            rationale="keyword_overlap",
                        )
                    )
        return links

    def _link_times_tables_to_objectives(
        self,
        *,
        times_table_focuses: list[CurriculumNode],
        objectives: list[CurriculumNode],
    ) -> list[CurriculumLink]:
        links: list[CurriculumLink] = []
        for focus in times_table_focuses:
            table_numbers = _extract_table_numbers(focus)
            for objective in objectives:
                objective_numbers = _extract_table_numbers(objective)
                same_year = bool(focus.year and objective.year and focus.year == objective.year)
                same_strand = bool(
                    focus.strand and objective.strand and focus.strand == objective.strand
                )
                matched_numbers = table_numbers.intersection(objective_numbers)
                if matched_numbers:
                    score = 0.8 + min(0.2, 0.05 * len(matched_numbers))
                    rationale = f"shared_tables:{','.join(map(str, sorted(matched_numbers)))}"
                elif same_year and same_strand:
                    score = 0.6
                    rationale = "same_year_and_strand"
                elif same_year:
                    score = 0.45
                    rationale = "same_year"
                else:
                    continue

                links.append(
                    CurriculumLink(
                        source_id=focus.id,
                        target_id=objective.id,
                        relation="times_table_to_objective",
                        score=score,
                        rationale=rationale,
                    )
                )
        return links


def build_and_persist_curriculum_links(raw_nodes: list[dict[str, Any]]) -> Path:
    """Convenience API used by normalization pipelines."""

    linker = CurriculumLinker()
    nodes = [CurriculumNode.from_mapping(raw) for raw in raw_nodes]
    linker.build_links(nodes)
    return linker.save_links()


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
