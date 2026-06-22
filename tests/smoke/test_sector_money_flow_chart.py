from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_sector_money_flow_chart_skill_outputs_html_replay(tmp_path: Path) -> None:
    manifest = json.loads((ROOT / "SKILLS_MANIFEST.json").read_text(encoding="utf-8"))
    skills = {skill["name"]: skill for skill in manifest["skills"]}
    skill = skills["sector-money-flow-chart"]
    skill_dir = ROOT / skill["path"]
    script = skill_dir / "scripts" / "generate_sector_money_flow_chart.py"

    assert skill_dir.is_dir()
    assert (skill_dir / "SKILL.md").is_file()
    assert "sector-money-flow-html-replay" in skill["provides"]
    assert "sector-money-flow-fullscreen-player" in skill["provides"]
    assert "sector-money-flow-trading-day-selector" in skill["provides"]
    assert '"sector-money-flow-chart"' in (ROOT / "tools" / "sync_runtime.ps1").read_text(encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--date",
            "2026-06-22",
            "--mode",
            "demo",
            "--out-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    paths = [Path(line.strip()).resolve() for line in result.stdout.splitlines() if line.strip()]
    html_path = tmp_path / "2026-06-22-sector-money-flow.html"
    svg_path = tmp_path / "2026-06-22-sector-money-flow.svg"
    csv_path = tmp_path / "2026-06-22-sector-money-flow.csv"
    quality_path = tmp_path / "2026-06-22-sector-money-flow-quality.md"
    index_path = tmp_path / "index.html"

    assert html_path.resolve() in paths
    assert index_path.resolve() in paths
    assert svg_path.is_file()
    assert csv_path.is_file()
    assert quality_path.is_file()

    html = html_path.read_text(encoding="utf-8")
    index_html = index_path.read_text(encoding="utf-8")
    quality = quality_path.read_text(encoding="utf-8")
    assert '<canvas id="chart"' in html
    assert 'id="chart-data"' in html
    assert "requestAnimationFrame" in html
    assert 'id="dateSelect"' in index_html
    assert "100vw" in index_html
    assert "100vh" in index_html
    assert "2026-06-22" in index_html
    assert "重新播放" in html
    assert "data_level: `demo`" in quality
    assert "html:" in quality
    assert "full_screen_player:" in quality


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temp_dir:
        test_sector_money_flow_chart_skill_outputs_html_replay(Path(temp_dir))
    print("sector money flow chart ok")
