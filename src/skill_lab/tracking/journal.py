"""Decision journal helpers for plans, reviews, and Harness results."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from skill_lab.shared.enums import EvalDomain, JournalEventType
from skill_lab.shared.schemas import DecisionJournalEntry, EvalResult, PlanOutcome, TomorrowPlan


def entry_from_plan(plan: TomorrowPlan, plan_id: str | None = None) -> DecisionJournalEntry:
    related_id = plan_id or f"plan:{plan.trade_date}"
    return DecisionJournalEntry(
        entry_id=f"{related_id}:created",
        event_type=JournalEventType.PLAN_CREATED,
        trade_date=plan.trade_date,
        created_at=now_iso(),
        title="Tomorrow plan created",
        summary=plan.summary,
        related_id=related_id,
        raw={"plan": plan.to_dict()},
    )


def entry_from_outcome(outcome: PlanOutcome) -> DecisionJournalEntry:
    return DecisionJournalEntry(
        entry_id=f"{outcome.plan_id}:outcome:{outcome.trade_date}",
        event_type=JournalEventType.PLAN_OUTCOME,
        trade_date=outcome.trade_date,
        created_at=now_iso(),
        title="Plan outcome recorded",
        summary=outcome.notes or outcome.status.value,
        related_id=outcome.plan_id,
        raw={"outcome": outcome.to_dict()},
    )


def entry_from_eval_result(result: EvalResult) -> DecisionJournalEntry:
    event_type = (
        JournalEventType.PLAN_EVALUATED
        if result.domain == EvalDomain.TOMORROW_PLAN
        else JournalEventType.DAILY_REVIEW_EVALUATED
        if result.domain == EvalDomain.DAILY_REVIEW
        else JournalEventType.RULE_UPDATE
    )
    return DecisionJournalEntry(
        entry_id=f"eval:{result.domain.value}:{result.sample_id}",
        event_type=event_type,
        trade_date=str(result.raw.get("trade_date") or ""),
        created_at=now_iso(),
        title=f"Evaluation result for {result.domain.value}",
        summary=result.notes or ("passed" if result.passed else "failed"),
        related_id=result.sample_id,
        score=result.score,
        error_types=list(result.error_types),
        suggested_fix=result.suggested_fix,
        raw={"eval_result": result.to_dict()},
    )


def append_jsonl(path: Path, entry: DecisionJournalEntry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

