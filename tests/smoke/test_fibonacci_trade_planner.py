from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_fibonacci_trade_planner_skill_and_script() -> None:
    manifest = json.loads((ROOT / "SKILLS_MANIFEST.json").read_text(encoding="utf-8"))
    skills = {skill["name"]: skill for skill in manifest["skills"]}
    skill = skills["a-share-fibonacci-trade-planner"]
    skill_dir = ROOT / skill["path"]
    script = skill_dir / "scripts" / "calculate_fibonacci_plan.py"

    assert skill_dir.is_dir()
    assert (skill_dir / "SKILL.md").is_file()
    assert script.is_file()
    assert "fibonacci-trade-plan" in skill["provides"]
    assert "index-sector-fibonacci-context" in skill["provides"]
    assert '"a-share-fibonacci-trade-planner"' in (ROOT / "tools" / "sync_runtime.ps1").read_text(encoding="utf-8")

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "Broad indices" in skill_text
    assert "Sector indices" in skill_text
    assert "When analyzing a single stock" in skill_text

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--low",
            "5.70",
            "--high",
            "8.02",
            "--current",
            "7.93",
            "--trend",
            "up",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(result.stdout)

    assert payload["retracements"]["0.382"] == 7.134
    assert payload["retracements"]["0.618"] == 6.586
    assert payload["extensions"]["1.272"] == 8.651
    assert payload["extensions"]["1.618"] == 9.454


if __name__ == "__main__":
    test_fibonacci_trade_planner_skill_and_script()
    print("fibonacci trade planner ok")
