from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.evaluation.judges import RequiredFieldJudge
from skill_lab.evaluation.reports import render_markdown
from skill_lab.evaluation.runner import run_judge
from skill_lab.shared.enums import EvalDomain
from skill_lab.shared.schemas import EvalSample


def test_required_field_judge_passes_complete_output():
    sample = EvalSample(
        sample_id="review-001",
        domain=EvalDomain.DAILY_REVIEW,
        input_data={"output": {"trade_date": "2026-06-05", "summary": "ok"}},
    )
    judge = RequiredFieldJudge(["trade_date", "summary"])
    result = judge.evaluate(sample)
    assert result.passed
    assert result.score == 100.0


def test_runner_builds_report_for_failed_sample():
    sample = EvalSample(
        sample_id="plan-001",
        domain=EvalDomain.TOMORROW_PLAN,
        input_data={"output": {"trade_date": "2026-06-05"}},
    )
    judge = RequiredFieldJudge(["trade_date", "items"])
    report = run_judge(judge, [sample], target_version="dev")
    text = render_markdown(report)
    assert report.total == 1
    assert report.passed == 0
    assert "MISSING_FIELD" in text


if __name__ == "__main__":
    test_required_field_judge_passes_complete_output()
    test_runner_builds_report_for_failed_sample()
