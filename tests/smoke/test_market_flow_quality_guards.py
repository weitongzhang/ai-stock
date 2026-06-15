from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_cls_theme_guards_reject_false_positive_contexts():
    module = load_module(
        "cls_plan",
        ROOT / "skills/content-collection/cls-telegraph-collector/scripts/analyze_cls_market_plan.py",
    )
    assert not module.themes_for_text("报告：今年夏令快消品或总体温和增长")
    assert not module.themes_for_text("俄称拦截和击毁超百架乌无人机")
    themes = [item["rule"]["theme"] for item in module.themes_for_text("国产GPU企业科创板IPO获通过")]
    assert "半导体/国产替代" in themes


def test_lhb_rows_are_aggregated_without_double_counting():
    module = load_module(
        "market_flow",
        ROOT / "skills/stock-selection/a-share-market-flow-analyst/scripts/analyze_market_flow.py",
    )
    rows = [
        {"名称": "样例股", "龙虎榜净买额": "100", "上榜原因": "原因A"},
        {"名称": "样例股", "龙虎榜净买额": "100", "上榜原因": "原因B"},
    ]
    aggregated = module.aggregate_lhb_rows(rows)
    assert len(aggregated) == 1
    assert module.lhb_net(aggregated[0]) == 100
    assert "原因A" in aggregated[0]["上榜原因"]
    assert "原因B" in aggregated[0]["上榜原因"]


def test_money_format_uses_wan_and_yi_units():
    module = load_module(
        "market_flow_money",
        ROOT / "skills/stock-selection/a-share-market-flow-analyst/scripts/analyze_market_flow.py",
    )
    assert module.format_money(1_537_055_380) == "15.37亿"
    assert module.format_money(8_800_000) == "880.00万"
    assert module.format_money(-125_000_000) == "-1.25亿"


if __name__ == "__main__":
    test_cls_theme_guards_reject_false_positive_contexts()
    test_lhb_rows_are_aggregated_without_double_counting()
    test_money_format_uses_wan_and_yi_units()
