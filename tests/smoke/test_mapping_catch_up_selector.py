import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "skills" / "stock-selection" / "a-share-mapping-catch-up-selector"


def test_mapping_catch_up_skill_files_exist():
    skill_md = SKILL_DIR / "SKILL.md"
    scoring = SKILL_DIR / "references" / "relationship-and-scoring.md"
    watch_pool = SKILL_DIR / "references" / "watch-pool.md"

    assert skill_md.exists()
    assert scoring.exists()
    assert watch_pool.exists()

    text = skill_md.read_text(encoding="utf-8")
    assert "name: a-share-mapping-catch-up-selector" in text
    assert "mapping catch-up" in text
    assert "relationship-and-scoring.md" in text
    assert "Long-term mapping watch pool" in text
    assert "核心分歧-映射承接" in text
    assert "观察期" in text
    assert "剔除" in text

    watch_text = watch_pool.read_text(encoding="utf-8")
    assert "铜冠铜箔 -> 铜陵有色" in watch_text
    assert "大族数控 -> 大族激光" in watch_text
    assert "Negative Marking Rules" in watch_text
    assert "核心分歧-映射承接" in watch_text


def test_mapping_catch_up_skill_registered_in_manifest():
    manifest = json.loads((ROOT / "SKILLS_MANIFEST.json").read_text(encoding="utf-8"))
    entry = next(
        skill
        for skill in manifest["skills"]
        if skill["name"] == "a-share-mapping-catch-up-selector"
    )

    assert entry["domain"] == "stock-selection"
    assert entry["path"] == "skills/stock-selection/a-share-mapping-catch-up-selector"
    assert "a-share-market-flow-analyst" in entry["coordinates"]
    assert "mapping-catch-up-candidate-list" in entry["provides"]
