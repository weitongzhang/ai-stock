from pathlib import Path
import subprocess
import sys
import tempfile
import json


ROOT = Path(__file__).resolve().parents[2]


def test_harness_cli_runs_markdown_report():
    dataset = ROOT / "examples" / "evals" / "datasets" / "tomorrow_plan" / "sample.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "run_harness_eval.py"),
            "--dataset",
            str(dataset),
            "--target-version",
            "smoke",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Evaluation Report" in result.stdout
    assert "Passed: 1" in result.stdout


def test_harness_cli_can_write_journal():
    dataset = ROOT / "examples" / "evals" / "datasets" / "tomorrow_plan" / "sample.jsonl"
    with tempfile.TemporaryDirectory() as tmp:
        journal = Path(tmp) / "journal.jsonl"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_harness_eval.py"),
                "--dataset",
                str(dataset),
                "--target-version",
                "smoke",
                "--journal",
                str(journal),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        rows = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["event_type"] == "plan_evaluated"


if __name__ == "__main__":
    test_harness_cli_runs_markdown_report()
    test_harness_cli_can_write_journal()
