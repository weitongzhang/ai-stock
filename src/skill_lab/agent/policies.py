"""Safety and degradation policies for the research agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from skill_lab.agent.state import AgentRequest, AgentTask
from skill_lab.market_data.quality import DataQualityReport


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)


class ResearchPolicy:
    """Keep the first agent read-only and evidence constrained."""

    allowed_tasks = set(AgentTask)

    def authorize(self, request: AgentRequest) -> PolicyDecision:
        reasons: list[str] = []
        if request.task not in self.allowed_tasks:
            reasons.append(f"unsupported task: {request.task}")
        if request.task == AgentTask.HOLDING_ANALYSIS:
            if not request.symbol:
                reasons.append("holding-analysis requires symbol")
            if request.cost is None or request.cost <= 0:
                reasons.append("holding-analysis requires a positive cost")
            if request.position_pct is not None and not 0 <= request.position_pct <= 100:
                reasons.append("position_pct must be within 0-100")
        elif not request.trade_date:
            reasons.append(f"{request.task.value} requires trade_date")
        return PolicyDecision(allowed=not reasons, reasons=reasons)

    def quality_allows(self, report: DataQualityReport, allow_warnings: bool) -> PolicyDecision:
        errors = [issue.message for issue in report.issues if issue.severity == "error"]
        warnings = [issue.message for issue in report.issues if issue.severity == "warning"]
        if errors:
            return PolicyDecision(False, errors)
        if warnings and not allow_warnings:
            return PolicyDecision(False, warnings)
        return PolicyDecision(True, warnings)
