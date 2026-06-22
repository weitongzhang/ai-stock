"""Build planning-safe institutional research context from MCP outputs."""

from __future__ import annotations

from typing import Any

from skill_lab.institutional_research.schemas import (
    InstitutionalResearchContext,
    InstitutionalResearchRecord,
)


MCP_SERVER_ROLES = {
    "juzi-fund": "fund-research",
    "juzi-manager": "manager-research",
    "juzi-stratos": "asset-allocation-and-quant-strategy",
    "juzi-skills": "developer-workflow",
    "juzi-report": "strategy-card",
}


def build_institutional_context(
    trade_date: str,
    records: list[InstitutionalResearchRecord],
) -> InstitutionalResearchContext:
    conflicts = [
        conflict
        for record in records
        for conflict in record.conflicts
    ]
    data_limits = []
    for record in records:
        if not record.evidence_date:
            data_limits.append(f"{record.source}:{record.topic} missing evidence_date")
        if record.confidence <= 0:
            data_limits.append(f"{record.source}:{record.topic} missing confidence")
    summary = summarize_records(records, conflicts)
    return InstitutionalResearchContext(
        trade_date=trade_date,
        records=records,
        summary=summary,
        conflicts=conflicts,
        data_limits=data_limits,
        raw={"record_count": len(records), "server_roles": MCP_SERVER_ROLES},
    )


def record_from_mcp_result(
    server: str,
    topic: str,
    result: dict[str, Any],
) -> InstitutionalResearchRecord:
    """Normalize a manually/tool-collected MCP result into evidence context."""

    role = MCP_SERVER_ROLES.get(server, "unknown")
    summary = str(result.get("summary") or result.get("conclusion") or "")
    evidence_date = str(result.get("evidence_date") or result.get("date") or "")
    return InstitutionalResearchRecord(
        source=server,
        topic=topic,
        evidence_date=evidence_date,
        summary=summary,
        supports=as_list(result.get("supports") or result.get("evidence")),
        cautions=as_list(result.get("cautions") or result.get("risks")),
        conflicts=as_list(result.get("conflicts")),
        required_follow_up=as_list(result.get("required_follow_up") or result.get("next_checks")),
        confidence=float(result.get("confidence") or 0.0),
        raw={"server_role": role, "result": result},
    )


def summarize_records(records: list[InstitutionalResearchRecord], conflicts: list[str]) -> str:
    if not records:
        return "no institutional research context"
    topics = ", ".join(f"{record.source}:{record.topic}" for record in records)
    suffix = f"; conflicts={len(conflicts)}" if conflicts else "; conflicts=0"
    return f"institutional records={len(records)} ({topics}){suffix}"


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    text = str(value)
    return [text] if text else []
