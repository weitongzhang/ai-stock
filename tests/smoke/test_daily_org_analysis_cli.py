from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_daily_org_analysis_cli_json_summary():
    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_daily_org_analysis.py",
            "--date",
            "2026-06-04",
            "--json",
            "--allow-quality-warnings",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    stdout = completed.stdout.decode("utf-8", errors="replace")
    data = json.loads(stdout)
    assert data["trade_date"] == "2026-06-04"
    assert data["market_regime"] == "attack"
    assert data["theme_count"] >= 3
    assert data["plan_items"] >= 3
    assert data["review_findings"] >= 3


def test_daily_org_analysis_cli_rejects_non_trade_date():
    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_daily_org_analysis.py",
            "--date",
            "2026-06-06",
            "--require-trade-date",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
    )
    stdout = completed.stdout.decode("utf-8", errors="replace")
    assert completed.returncode == 4
    assert "not a trade date" in stdout


if __name__ == "__main__":
    test_daily_org_analysis_cli_json_summary()
    test_daily_org_analysis_cli_rejects_non_trade_date()
