#!/usr/bin/env python
"""Run a minimal, auditable plan-to-outcome research loop."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.agent import AgentRequest, AgentTask, ResearchAgentController
from skill_lab.shared.enums import EvalDomain, PlanOutcomeStatus
from skill_lab.shared.schemas import EvalResult, PlanOutcome, TomorrowPlan
from skill_lab.tracking.journal import (
    append_jsonl,
    entry_from_eval_result,
    entry_from_outcome,
    entry_from_plan,
    load_jsonl,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal auditable research loop example.")
    parser.add_argument("--plan-date", default="2026-06-04")
    parser.add_argument("--outcome-date", default="2026-06-05")
    parser.add_argument("--out-dir", default="examples/audit-loop/output")
    parser.add_argument(
        "--fallback-latest",
        action="store_true",
        help="Use the latest earlier date with all required offline inputs.",
    )
    args = parser.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    journal_path = out_dir / "decision-journal.jsonl"
    journal_path.unlink(missing_ok=True)

    requested_date = args.plan_date
    data_date = requested_date
    missing_inputs = required_inputs(ROOT, data_date)
    if missing_inputs and args.fallback_latest:
        fallback = latest_complete_input_date(ROOT, requested_date)
        if fallback:
            data_date = fallback
            missing_inputs = []
    elif args.fallback_latest and not daily_inputs_pass_quality(ROOT, data_date):
        fallback = latest_complete_input_date(ROOT, previous_date(requested_date))
        if fallback:
            data_date = fallback

    run_id = f"daily:{requested_date}"
    plan_id = f"plan:{requested_date}"
    if missing_inputs:
        audit = build_blocked_summary(run_id, plan_id, requested_date, missing_inputs)
        write_audit_outputs(out_dir, audit)
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 2

    controller = ResearchAgentController(ROOT)
    result = controller.run(
        AgentRequest(
            task=AgentTask.TOMORROW_PLAN,
            trade_date=data_date,
            allow_quality_warnings=True,
        )
    )
    result_data = result.to_dict()
    plan_data = result_data.get("output", {}).get("tomorrow_plan")
    if not plan_data:
        audit = build_agent_failure_summary(run_id, plan_id, requested_date, data_date, result_data)
        write_audit_outputs(out_dir, audit)
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 2
    plan = plan_from_dict(plan_data)
    attach_audit_metadata(plan, run_id, plan_id, requested_date, data_date)
    append_jsonl(journal_path, entry_from_plan(plan, plan_id))

    outcome = simulate_outcome(plan, plan_id, args.outcome_date, run_id)
    append_jsonl(journal_path, entry_from_outcome(outcome))

    evaluation = evaluate_closed_loop(plan, outcome, run_id)
    append_jsonl(journal_path, entry_from_eval_result(evaluation))

    audit = build_audit_summary(plan, outcome, evaluation, journal_path, run_id, plan_id)
    audit["requested_date"] = requested_date
    audit["data_date"] = data_date
    audit["used_fallback"] = data_date != requested_date
    write_audit_outputs(out_dir, audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


def plan_from_dict(data: dict) -> TomorrowPlan:
    from skill_lab.shared.schemas import TomorrowPlanItem
    from skill_lab.shared.serialization import parse_enum
    from skill_lab.shared.enums import ActionLevel, MarketRegime

    items = [
        TomorrowPlanItem(
            theme=item["theme"],
            priority=int(item["priority"]),
            action=parse_enum(ActionLevel, item.get("action"), ActionLevel.UNKNOWN),
            candidates=list(item.get("candidates") or []),
            confirm_signal=item.get("confirm_signal", ""),
            give_up_signal=item.get("give_up_signal", ""),
            position_constraint=item.get("position_constraint", ""),
            reasons=list(item.get("reasons") or []),
            raw=dict(item.get("raw") or {}),
        )
        for item in data.get("items") or []
    ]
    return TomorrowPlan(
        trade_date=data["trade_date"],
        generated_at=data.get("generated_at", ""),
        market_regime=parse_enum(MarketRegime, data.get("market_regime"), MarketRegime.UNKNOWN),
        summary=data.get("summary", ""),
        items=items,
        data_limits=list(data.get("data_limits") or []),
        raw=dict(data.get("raw") or {}),
    )


def attach_audit_metadata(
    plan: TomorrowPlan,
    run_id: str,
    plan_id: str,
    requested_date: str,
    data_date: str,
) -> None:
    plan.raw["audit"] = {
        "run_id": run_id,
        "plan_id": plan_id,
        "producer": "ResearchAgentController.tomorrow-plan",
        "state": "PLANNED",
        "requested_date": requested_date,
        "data_date": data_date,
    }
    for item in plan.items:
        item.raw["audit"] = {
            "run_id": run_id,
            "plan_id": plan_id,
            "item_id": f"{plan_id}:item:{item.priority}",
            "state": "OBSERVING",
        }


def simulate_outcome(
    plan: TomorrowPlan,
    plan_id: str,
    outcome_date: str,
    run_id: str,
) -> PlanOutcome:
    triggered = [plan.items[0].raw["audit"]["item_id"]] if plan.items else []
    invalidated = [plan.items[-1].raw["audit"]["item_id"]] if len(plan.items) > 1 else []
    return PlanOutcome(
        plan_id=plan_id,
        trade_date=outcome_date,
        status=PlanOutcomeStatus.REVIEW_REQUIRED,
        triggered_items=triggered,
        invalidated_items=invalidated,
        notes="Example outcome: first priority triggered; lowest priority invalidated; human review required.",
        raw={
            "run_id": run_id,
            "source": "simulated-example",
            "state": "REVIEWED",
            "warning": "Replace simulated outcomes with observed market evidence in production.",
        },
    )


def evaluate_closed_loop(plan: TomorrowPlan, outcome: PlanOutcome, run_id: str) -> EvalResult:
    item_ids = {item.raw["audit"]["item_id"] for item in plan.items}
    resolved_ids = set(outcome.triggered_items + outcome.invalidated_items)
    coverage = len(resolved_ids & item_ids) / len(item_ids) if item_ids else 0.0
    has_conditions = all(item.confirm_signal and item.give_up_signal for item in plan.items)
    score = round(50 * coverage + 25 * float(has_conditions) + 25 * float(bool(outcome.notes)), 1)
    return EvalResult(
        sample_id=f"audit:{plan.trade_date}",
        domain=EvalDomain.TOMORROW_PLAN,
        target_version="audit-loop-example-v1",
        judge_version="deterministic-closure-v1",
        format_ok=True,
        field_complete=has_conditions,
        score=score,
        passed=coverage == 1.0 and has_conditions,
        evidence_quality=coverage * 100,
        actionability=100 if has_conditions else 50,
        risk_control=100 if has_conditions else 50,
        notes=f"resolved {len(resolved_ids & item_ids)}/{len(item_ids)} plan items",
        suggested_fix="Record an outcome for every unresolved plan item.",
        raw={"trade_date": outcome.trade_date, "run_id": run_id, "closure_coverage": coverage},
    )


def build_audit_summary(
    plan: TomorrowPlan,
    outcome: PlanOutcome,
    evaluation: EvalResult,
    journal_path: Path,
    run_id: str,
    plan_id: str,
) -> dict:
    rows = load_jsonl(journal_path)
    resolved = set(outcome.triggered_items + outcome.invalidated_items)
    items = [
        {
            "item_id": item.raw["audit"]["item_id"],
            "theme": item.theme,
            "action": item.action.value,
            "confirm_signal": item.confirm_signal,
            "give_up_signal": item.give_up_signal,
            "closure": (
                "triggered"
                if item.raw["audit"]["item_id"] in outcome.triggered_items
                else "invalidated"
                if item.raw["audit"]["item_id"] in outcome.invalidated_items
                else "unresolved"
            ),
        }
        for item in plan.items
    ]
    return {
        "run_id": run_id,
        "plan_id": plan_id,
        "state": "CLOSED" if evaluation.passed else "EVALUATED_WITH_GAPS",
        "journal_event_count": len(rows),
        "journal_events": [row["event_type"] for row in rows],
        "plan_summary": plan.summary,
        "outcome_summary": outcome.notes,
        "closure": {
            "resolved_items": len(resolved),
            "total_items": len(plan.items),
            "coverage_pct": round(100 * len(resolved) / len(plan.items), 1) if plan.items else 0.0,
        },
        "evaluation": evaluation.to_dict(),
        "items": items,
    }


def render_markdown(audit: dict) -> str:
    if audit["state"] == "BLOCKED":
        lines = [
            "# Minimal Auditable Research Loop",
            "",
            f"- Run ID: `{audit['run_id']}`",
            f"- Requested date: `{audit['requested_date']}`",
            f"- State: `{audit['state']}`",
            f"- Reason: `{audit['reason']}`",
            "",
            "## Missing Inputs",
            "",
        ]
        lines.extend(f"- `{path}`" for path in audit["missing_inputs"])
        lines.extend(["", "## Required Action", "", audit["required_action"], ""])
        return "\n".join(lines)

    lines = [
        "# Minimal Auditable Research Loop",
        "",
        f"- Run ID: `{audit['run_id']}`",
        f"- Plan ID: `{audit['plan_id']}`",
        f"- State: `{audit['state']}`",
        f"- Closure coverage: `{audit['closure']['coverage_pct']}%`",
        f"- Evaluation score: `{audit['evaluation']['score']}`",
        "",
        "## Journal",
        "",
    ]
    lines.extend(f"- `{event}`" for event in audit["journal_events"])
    lines.extend(["", "## Plan Items", ""])
    for item in audit["items"]:
        lines.extend(
            [
                f"### {item['item_id']} - {item['theme']}",
                "",
                f"- Action: `{item['action']}`",
                f"- Confirmation: {item['confirm_signal']}",
                f"- Invalidation: {item['give_up_signal']}",
                f"- Closure: `{item['closure']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "This example intentionally leaves some plan items unresolved. "
            "The audit score exposes the gap instead of silently treating the workflow as complete.",
            "",
        ]
    )
    return "\n".join(lines)


def required_inputs(root: Path, trade_date: str) -> list[str]:
    relative_paths = [
        Path("examples/market/market-breadth") / f"{trade_date}-market-breadth.csv",
        Path("examples/market/index-environment") / f"{trade_date}-index-environment.csv",
        Path("examples/market/market-flow") / f"{trade_date}-market-flow.csv",
    ]
    return [str(path) for path in relative_paths if not (root / path).exists()]


def latest_complete_input_date(root: Path, requested_date: str) -> str:
    candidates = []
    for path in (root / "examples" / "market" / "market-flow").glob("*-market-flow.csv"):
        trade_date = path.name.removesuffix("-market-flow.csv")
        try:
            datetime.strptime(trade_date, "%Y-%m-%d")
        except ValueError:
            continue
        if trade_date <= requested_date and not required_inputs(root, trade_date) and daily_inputs_pass_quality(root, trade_date):
            candidates.append(trade_date)
    return max(candidates, default="")


def daily_inputs_pass_quality(root: Path, trade_date: str) -> bool:
    result = ResearchAgentController(root).run(
        AgentRequest(
            task=AgentTask.TOMORROW_PLAN,
            trade_date=trade_date,
            allow_quality_warnings=True,
        )
    )
    return result.to_dict()["status"] in {"completed", "degraded"}


def previous_date(value: str) -> str:
    from datetime import timedelta

    return (datetime.strptime(value, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")


def build_blocked_summary(
    run_id: str,
    plan_id: str,
    requested_date: str,
    missing_inputs: list[str],
) -> dict:
    return {
        "run_id": run_id,
        "plan_id": plan_id,
        "requested_date": requested_date,
        "data_date": "",
        "used_fallback": False,
        "state": "BLOCKED",
        "reason": "required_inputs_missing",
        "missing_inputs": missing_inputs,
        "required_action": "Generate the missing normalized daily input files, then rerun.",
        "journal_event_count": 0,
        "journal_events": [],
        "items": [],
    }


def build_agent_failure_summary(
    run_id: str,
    plan_id: str,
    requested_date: str,
    data_date: str,
    result: dict,
) -> dict:
    return {
        "run_id": run_id,
        "plan_id": plan_id,
        "requested_date": requested_date,
        "data_date": data_date,
        "used_fallback": data_date != requested_date,
        "state": "BLOCKED",
        "reason": "research_agent_failed",
        "missing_inputs": list(result.get("data_limits") or []),
        "required_action": result.get("summary") or "Inspect the research agent failure.",
        "agent_result": result,
        "journal_event_count": 0,
        "journal_events": [],
        "items": [],
    }


def write_audit_outputs(out_dir: Path, audit: dict) -> None:
    (out_dir / "audit-summary.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit-summary.md").write_text(render_markdown(audit), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
