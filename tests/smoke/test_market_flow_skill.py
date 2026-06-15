from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]


def test_market_flow_skill_offline_writes_audited_result():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        out_dir = Path(tmp).relative_to(ROOT)
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skills/stock-selection/a-share-market-flow-analyst/scripts/run_market_flow_skill.py"),
                "--date",
                "2026-06-04",
                "--offline",
                "--out-dir",
                str(out_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode in {0, 2}, completed.stderr
        result = (Path(tmp) / "skill-result.json").read_text(encoding="utf-8")
        assert '"skill": "a-share-market-flow-analyst"' in result
        assert '"trade_date": "2026-06-04"' in result


if __name__ == "__main__":
    test_market_flow_skill_offline_writes_audited_result()
