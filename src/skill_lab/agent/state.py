"""State objects used by the deterministic research agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from skill_lab.shared.serialization import to_plain


class AgentTask(str, Enum):
    POST_MARKET_REVIEW = "post-market-review"
    TOMORROW_PLAN = "tomorrow-plan"
    HOLDING_ANALYSIS = "holding-analysis"


class AgentRunStatus(str, Enum):
    COMPLETED = "completed"
    DEGRADED = "degraded"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass(slots=True)
class AgentRequest:
    task: AgentTask
    trade_date: str = ""
    symbol: str = ""
    name: str = ""
    cost: float | None = None
    position_pct: float | None = None
    allow_quality_warnings: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentStep:
    name: str
    tool: str
    status: str
    summary: str = ""


@dataclass(slots=True)
class AgentResult:
    task: AgentTask
    status: AgentRunStatus
    summary: str
    output: dict[str, Any] = field(default_factory=dict)
    steps: list[AgentStep] = field(default_factory=list)
    data_limits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)
