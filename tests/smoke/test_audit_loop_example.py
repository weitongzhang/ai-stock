from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]


def test_audit_loop_example_writes_traceable_outputs():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        out_dir = Path(tmp).relative_to(ROOT)
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_audit_loop_example.py"),
                "--out-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        journal = Path(tmp) / "decision-journal.jsonl"
        summary = Path(tmp) / "audit-summary.md"
        assert journal.exists()
        assert summary.exists()
        assert len(journal.read_text(encoding="utf-8").splitlines()) == 3
        text = summary.read_text(encoding="utf-8")
        assert "EVALUATED_WITH_GAPS" in text
        assert "Closure coverage" in text


def test_audit_loop_example_reports_missing_inputs_without_traceback():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        out_dir = Path(tmp).relative_to(ROOT)
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_audit_loop_example.py"),
                "--plan-date",
                "2099-01-05",
                "--out-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 2
        assert "Traceback" not in completed.stderr
        text = (Path(tmp) / "audit-summary.md").read_text(encoding="utf-8")
        assert "BLOCKED" in text
        assert "required_inputs_missing" in text


def test_audit_loop_example_can_use_latest_complete_inputs():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        out_dir = Path(tmp).relative_to(ROOT)
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_audit_loop_example.py"),
                "--plan-date",
                "2026-06-15",
                "--out-dir",
                str(out_dir),
                "--fallback-latest",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        text = (Path(tmp) / "audit-summary.json").read_text(encoding="utf-8")
        assert '"requested_date": "2026-06-15"' in text
        assert '"data_date": "2026-06-04"' in text
        assert '"used_fallback": true' in text


if __name__ == "__main__":
    test_audit_loop_example_writes_traceable_outputs()
    test_audit_loop_example_reports_missing_inputs_without_traceback()
    test_audit_loop_example_can_use_latest_complete_inputs()
