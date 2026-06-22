"""Schemas for external institutional research context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from skill_lab.shared.schemas import Serializable


@dataclass(slots=True)
class InstitutionalResearchRecord(Serializable):
    source: str
    topic: str
    evidence_date: str = ""
    summary: str = ""
    supports: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    required_follow_up: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class InstitutionalResearchContext(Serializable):
    trade_date: str
    records: list[InstitutionalResearchRecord] = field(default_factory=list)
    summary: str = ""
    conflicts: list[str] = field(default_factory=list)
    data_limits: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
