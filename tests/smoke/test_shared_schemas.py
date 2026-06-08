from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.shared.enums import EvalDomain, MarketRegime
from skill_lab.shared.schemas import EvalSample, MarketRegimeResult, PerspectiveAnalysis, TomorrowPlan


def test_schema_serialization_roundtrip_shape():
    regime = MarketRegimeResult(
        trade_date="2026-06-05",
        regime=MarketRegime.STRUCTURAL_REPAIR,
        score=72.5,
        reasons=["breadth improved"],
    )
    data = regime.to_dict()
    assert data["regime"] == "structural_repair"
    assert data["reasons"] == ["breadth improved"]


def test_eval_sample_schema():
    sample = EvalSample(
        sample_id="tp-001",
        domain=EvalDomain.TOMORROW_PLAN,
        input_data={"output": TomorrowPlan(trade_date="2026-06-05").to_dict()},
    )
    assert sample.to_dict()["domain"] == "tomorrow_plan"


def test_perspective_analysis_serialization():
    perspective = PerspectiveAnalysis(
        source="chen-xiaoqun-perspective",
        focus="theme-mainline-and-leader",
        conflicts=["leader evidence missing"],
        confidence=0.55,
    )
    data = perspective.to_dict()
    assert data["source"] == "chen-xiaoqun-perspective"
    assert data["conflicts"] == ["leader evidence missing"]


if __name__ == "__main__":
    test_schema_serialization_roundtrip_shape()
    test_eval_sample_schema()
    test_perspective_analysis_serialization()
