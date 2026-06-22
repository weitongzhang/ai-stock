from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.agent import AgentRequest, AgentTask, ResearchAgentController
from skill_lab.shared.enums import BarSpan, DataSource
from skill_lab.shared.schemas import Bar


class FakeBarProvider:
    def get_bars(self, symbol, span=BarSpan.DAY1, limit=250, until=None):
        bars = []
        for index in range(60):
            close = 50 - index * 0.25
            bars.append(
                Bar(
                    symbol=symbol,
                    timestamp=f"2026-05-{index + 1:02d}T15:00:00",
                    open=close + 0.2,
                    high=close + 0.5,
                    low=close - 0.5,
                    close=close,
                    volume=1000 + index,
                    amount=100000 + index,
                    source=DataSource.SAMPLE,
                )
            )
        return bars

    def get_market_breadth(self, trade_date):
        raise NotImplementedError

    def get_index_environment(self, trade_date):
        raise NotImplementedError

    def get_theme_scores(self, trade_date):
        raise NotImplementedError


def test_research_agent_builds_tomorrow_plan():
    controller = ResearchAgentController(ROOT)
    result = controller.run(
        AgentRequest(
            task=AgentTask.TOMORROW_PLAN,
            trade_date="2026-06-04",
            allow_quality_warnings=True,
        )
    )
    data = result.to_dict()
    assert data["status"] in {"completed", "degraded"}
    assert data["output"]["tomorrow_plan"]["items"]
    assert len(data["steps"]) >= 3


def test_research_agent_builds_post_market_review():
    controller = ResearchAgentController(ROOT)
    result = controller.run(
        AgentRequest(
            task=AgentTask.POST_MARKET_REVIEW,
            trade_date="2026-06-04",
            allow_quality_warnings=True,
        )
    )
    data = result.to_dict()
    assert data["output"]["daily_review"]["findings"]
    assert data["output"]["tomorrow_plan"]["items"]


def test_research_agent_builds_holding_risk_plan():
    controller = ResearchAgentController(ROOT, bar_provider=FakeBarProvider())
    result = controller.run(
        AgentRequest(
            task=AgentTask.HOLDING_ANALYSIS,
            symbol="600580.SH",
            name="卧龙电驱",
            cost=42.5,
            position_pct=60,
        )
    )
    analysis = result.to_dict()["output"]["holding_analysis"]
    assert analysis["trend"] == "down"
    assert analysis["action"] == "reduce-on-rebound"
    assert analysis["invalidation"]


def test_research_agent_rejects_missing_holding_cost():
    controller = ResearchAgentController(ROOT, bar_provider=FakeBarProvider())
    result = controller.run(AgentRequest(task=AgentTask.HOLDING_ANALYSIS, symbol="600580.SH"))
    assert result.to_dict()["status"] == "rejected"


if __name__ == "__main__":
    test_research_agent_builds_tomorrow_plan()
    test_research_agent_builds_post_market_review()
    test_research_agent_builds_holding_risk_plan()
    test_research_agent_rejects_missing_holding_cost()
