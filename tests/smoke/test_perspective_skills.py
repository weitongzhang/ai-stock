from __future__ import annotations

import json
import locale
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_search(skill_dir: Path, query: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            str(skill_dir / "scripts" / "search_knowledge.py"),
            query,
            "--limit",
            "2",
        ],
        cwd=skill_dir,
        check=True,
        capture_output=True,
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )
    assert result.stdout.strip()
    return result.stdout


def test_blogger_perspective_skills_are_registered_and_searchable() -> None:
    manifest = json.loads((ROOT / "SKILLS_MANIFEST.json").read_text(encoding="utf-8"))
    skills = {skill["name"]: skill for skill in manifest["skills"]}

    expected = {
        "chen-xiaoqun-perspective": ROOT
        / "skills"
        / "stock-selection"
        / "chen-xiaoqun-perspective",
        "model-xiansheng-perspective": ROOT
        / "skills"
        / "methodology"
        / "model-xiansheng-perspective",
    }

    for name, skill_dir in expected.items():
        assert name in skills
        assert skill_dir.is_dir()
        assert (skill_dir / "SKILL.md").read_text(encoding="utf-8").startswith("---")
        assert (skill_dir / "agents" / "openai.yaml").is_file()
        assert (skill_dir / "references" / "knowledge" / "core-viewpoints.md").is_file()
        assert (skill_dir / "references" / "knowledge" / "topic-index.md").is_file()
        assert (skill_dir / "scripts" / "search_knowledge.py").is_file()

    chen_output = _run_search(expected["chen-xiaoqun-perspective"], "龙头 题材")
    model_output = _run_search(expected["model-xiansheng-perspective"], "主要矛盾 质变")
    sync_script = (ROOT / "tools" / "sync_runtime.ps1").read_text(encoding="utf-8")

    assert "CX-" in chen_output
    assert "MX-" in model_output
    assert '"chen-xiaoqun-perspective"' in sync_script
    assert '"model-xiansheng-perspective"' in sync_script


if __name__ == "__main__":
    test_blogger_perspective_skills_are_registered_and_searchable()
    print("perspective skills ok")
