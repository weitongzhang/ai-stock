"""Deterministic controller for the first research-agent runtime."""

from __future__ import annotations

from pathlib import Path

from skill_lab.agent.policies import ResearchPolicy
from skill_lab.agent.state import AgentRequest, AgentResult, AgentRunStatus, AgentStep, AgentTask
from skill_lab.agent.tool_registry import ToolRegistry
from skill_lab.market_analysis.breadth import classify_breadth
from skill_lab.market_analysis.index_environment import summarize_index_environment
from skill_lab.market_analysis.regime import classify_market_regime
from skill_lab.market_data.file_provider import FileProvider
from skill_lab.market_data.providers import DataProvider
from skill_lab.market_data.quality import check_bars
from skill_lab.planning.daily_review import build_daily_review
from skill_lab.planning.tomorrow_plan import build_tomorrow_plan
from skill_lab.sector_analysis.strength import summarize_theme_strength
from skill_lab.shared.enums import BarSpan


class ResearchAgentController:
    """Route approved research tasks through tested deterministic services."""

    def __init__(
        self,
        root: Path | str,
        daily_provider: FileProvider | None = None,
        bar_provider: DataProvider | None = None,
        policy: ResearchPolicy | None = None,
    ) -> None:
        self.root = Path(root)
        self.daily_provider = daily_provider or FileProvider(self.root)
        self.bar_provider = bar_provider
        self.policy = policy or ResearchPolicy()
        self.tools = ToolRegistry()
        self._register_tools()

    def run(self, request: AgentRequest) -> AgentResult:
        decision = self.policy.authorize(request)
        if not decision.allowed:
            return AgentResult(
                task=request.task,
                status=AgentRunStatus.REJECTED,
                summary="request rejected by research policy",
                data_limits=decision.reasons,
            )
        try:
            if request.task == AgentTask.TOMORROW_PLAN:
                return self._run_tomorrow_plan(request)
            if request.task == AgentTask.POST_MARKET_REVIEW:
                return self._run_post_market_review(request)
            if request.task == AgentTask.HOLDING_ANALYSIS:
                return self._run_holding_analysis(request)
        except (FileNotFoundError, NotImplementedError, ValueError) as exc:
            return AgentResult(
                task=request.task,
                status=AgentRunStatus.FAILED,
                summary=str(exc),
                data_limits=[str(exc)],
            )
        return AgentResult(request.task, AgentRunStatus.REJECTED, "unsupported task")

    def _register_tools(self) -> None:
        self.tools.register("daily-quality", self.daily_provider.check_daily_inputs)
        self.tools.register("market-breadth", self.daily_provider.get_market_breadth)
        self.tools.register("index-environment", self.daily_provider.get_index_environment)
        self.tools.register("theme-scores", self.daily_provider.get_theme_scores)
        self.tools.register("classify-breadth", classify_breadth)
        self.tools.register("summarize-indexes", summarize_index_environment)
        self.tools.register("classify-market", classify_market_regime)
        self.tools.register("summarize-themes", summarize_theme_strength)
        self.tools.register("build-tomorrow-plan", build_tomorrow_plan)
        self.tools.register("build-daily-review", build_daily_review)
        if self.bar_provider is not None:
            self.tools.register("stock-bars", self.bar_provider.get_bars)

    def _daily_context(self, request: AgentRequest):
        steps: list[AgentStep] = []
        quality = self.tools.call("daily-quality", trade_date=request.trade_date)
        steps.append(AgentStep("check daily inputs", "daily-quality", "completed", quality.subject))
        decision = self.policy.quality_allows(quality, request.allow_quality_warnings)
        if not decision.allowed:
            return None, steps, decision.reasons
        breadth = self.tools.call("market-breadth", trade_date=request.trade_date)
        indexes = self.tools.call("index-environment", trade_date=request.trade_date)
        theme_rows = self.tools.call("theme-scores", trade_date=request.trade_date)
        steps.append(AgentStep("load normalized daily data", "daily providers", "completed"))
        market = self.tools.call(
            "classify-market",
            breadth=self.tools.call("classify-breadth", breadth=breadth),
            index_summary=self.tools.call("summarize-indexes", rows=indexes),
        )
        themes = self.tools.call("summarize-themes", themes=theme_rows)
        steps.append(AgentStep("classify market and themes", "analysis services", "completed"))
        return (market, themes), steps, decision.reasons

    def _run_tomorrow_plan(self, request: AgentRequest) -> AgentResult:
        context, steps, limits = self._daily_context(request)
        if context is None:
            return AgentResult(request.task, AgentRunStatus.FAILED, "daily input quality rejected", steps=steps, data_limits=limits)
        market, themes = context
        plan = self.tools.call("build-tomorrow-plan", trade_date=request.trade_date, market=market, themes=themes)
        steps.append(AgentStep("build tomorrow plan", "build-tomorrow-plan", "completed", plan.summary))
        status = AgentRunStatus.DEGRADED if limits else AgentRunStatus.COMPLETED
        return AgentResult(request.task, status, plan.summary, {"tomorrow_plan": plan.to_dict()}, steps, limits)

    def _run_post_market_review(self, request: AgentRequest) -> AgentResult:
        context, steps, limits = self._daily_context(request)
        if context is None:
            return AgentResult(request.task, AgentRunStatus.FAILED, "daily input quality rejected", steps=steps, data_limits=limits)
        market, themes = context
        plan = self.tools.call("build-tomorrow-plan", trade_date=request.trade_date, market=market, themes=themes)
        review = self.tools.call(
            "build-daily-review",
            trade_date=request.trade_date,
            market=market,
            themes=themes,
            tomorrow_plan=plan,
            data_limits=limits,
        )
        steps.append(AgentStep("build post-market review", "build-daily-review", "completed", review.summary))
        status = AgentRunStatus.DEGRADED if limits else AgentRunStatus.COMPLETED
        return AgentResult(
            request.task,
            status,
            review.summary,
            {"daily_review": review.to_dict(), "tomorrow_plan": plan.to_dict()},
            steps,
            limits,
        )

    def _run_holding_analysis(self, request: AgentRequest) -> AgentResult:
        if self.bar_provider is None:
            raise ValueError("holding-analysis requires a configured bar provider")
        bars = self.tools.call("stock-bars", symbol=request.symbol, span=BarSpan.DAY1, limit=60)
        quality = check_bars(bars, symbol=request.symbol)
        decision = self.policy.quality_allows(quality, request.allow_quality_warnings)
        steps = [AgentStep("load and validate stock bars", "stock-bars", "completed", quality.subject)]
        if not decision.allowed:
            return AgentResult(request.task, AgentRunStatus.FAILED, "stock bar quality rejected", steps=steps, data_limits=decision.reasons)
        analysis = build_holding_analysis(
            request.symbol,
            request.name,
            float(request.cost),
            request.position_pct,
            bars,
        )
        steps.append(AgentStep("build holding risk plan", "holding structure analysis", "completed", analysis["action"]))
        status = AgentRunStatus.DEGRADED if decision.reasons else AgentRunStatus.COMPLETED
        return AgentResult(request.task, status, analysis["summary"], {"holding_analysis": analysis}, steps, decision.reasons)


def build_holding_analysis(symbol: str, name: str, cost: float, position_pct: float | None, bars) -> dict:
    closes = [bar.close for bar in bars]
    latest = bars[-1]
    ma5 = average(closes[-5:])
    ma10 = average(closes[-10:])
    ma20 = average(closes[-20:])
    recent_lows = [bar.low for bar in bars[-20:]]
    recent_highs = [bar.high for bar in bars[-20:]]
    support = min(recent_lows)
    resistance = max(ma5, ma10)
    trend = "down" if latest.close < ma5 < ma10 and latest.close < ma20 else "repair" if latest.close < ma20 else "up"
    pnl_pct = (latest.close / cost - 1) * 100
    heavy = position_pct is not None and position_pct >= 50
    if trend == "down":
        action = "reduce-on-rebound" if heavy or pnl_pct <= -10 else "hold-with-stop"
    elif trend == "repair":
        action = "hold-and-observe"
    else:
        action = "hold"
    return {
        "symbol": symbol,
        "name": name,
        "trade_date": latest.timestamp[:10],
        "cost": round(cost, 4),
        "position_pct": position_pct,
        "close": latest.close,
        "pnl_pct": round(pnl_pct, 2),
        "trend": trend,
        "action": action,
        "support": round(support, 4),
        "resistance": round(resistance, 4),
        "ma5": round(ma5, 4),
        "ma10": round(ma10, 4),
        "ma20": round(ma20, 4),
        "invalidation": f"close below {support:.2f}",
        "confirmation": f"close above {resistance:.2f} and hold",
        "summary": f"{symbol} trend={trend}; action={action}; pnl={pnl_pct:.2f}%",
    }


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
