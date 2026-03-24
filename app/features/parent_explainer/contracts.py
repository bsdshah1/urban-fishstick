"""API contracts for the parent explainer feature."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.services import CalculationMethodService, ParentCommunicationService


@dataclass(frozen=True)
class ParentExplainerRequest:
    year_group: str
    topic: str
    reading_level: str = "plain"
    locale: str = "en-GB"


@dataclass(frozen=True)
class ParentExplainerResponse:
    summary: str
    method_steps: Sequence[str]
    misconceptions: Sequence[str]
    home_practice_tips: Sequence[str]


@dataclass(frozen=True)
class ParentExplainerDependencies:
    calculation_method_service: CalculationMethodService
    communication_service: ParentCommunicationService
