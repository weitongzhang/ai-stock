from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.evaluation.datasets import load_jsonl
from skill_lab.evaluation.judges import RequiredFieldJudge
from skill_lab.evaluation.reports import render_markdown
from skill_lab.evaluation.runner import run_judge


def test_tomorrow_plan_eval_dataset_runs():
    samples = load_jsonl(ROOT / "examples" / "evals" / "datasets" / "tomorrow_plan" / "sample.jsonl")
    required = samples[0].ground_truth["required_fields"]
    report = run_judge(RequiredFieldJudge(required), samples, target_version="smoke")
    assert report.total == 1
    assert report.passed == 1
    assert "Average score" in render_markdown(report)


def test_daily_review_eval_dataset_runs():
    samples = load_jsonl(ROOT / "examples" / "evals" / "datasets" / "daily_review" / "sample.jsonl")
    required = samples[0].ground_truth["required_fields"]
    report = run_judge(RequiredFieldJudge(required), samples, target_version="smoke")
    assert report.total == 1
    assert report.passed == 1


if __name__ == "__main__":
    test_tomorrow_plan_eval_dataset_runs()
    test_daily_review_eval_dataset_runs()
