from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.shared.enums import EvalDomain, PlanOutcomeStatus
from skill_lab.shared.schemas import EvalResult, PlanOutcome, TomorrowPlan
from skill_lab.tracking.journal import (
    append_jsonl,
    entry_from_eval_result,
    entry_from_outcome,
    entry_from_plan,
    load_jsonl,
)


def test_journal_entries_can_be_persisted():
    plan = TomorrowPlan(trade_date="2026-06-04", summary="smoke plan")
    outcome = PlanOutcome(
        plan_id="plan:2026-06-04",
        trade_date="2026-06-05",
        status=PlanOutcomeStatus.TRIGGERED,
        notes="first item triggered",
    )
    eval_result = EvalResult(
        sample_id="tp-001",
        domain=EvalDomain.TOMORROW_PLAN,
        score=100,
        passed=True,
        raw={"trade_date": "2026-06-04"},
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "journal.jsonl"
        append_jsonl(path, entry_from_plan(plan))
        append_jsonl(path, entry_from_outcome(outcome))
        append_jsonl(path, entry_from_eval_result(eval_result))
        rows = load_jsonl(path)

    assert len(rows) == 3
    assert rows[0]["event_type"] == "plan_created"
    assert rows[1]["event_type"] == "plan_outcome"
    assert rows[2]["event_type"] == "plan_evaluated"


if __name__ == "__main__":
    test_journal_entries_can_be_persisted()
