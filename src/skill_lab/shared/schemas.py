"""Core dataclass schemas shared by trading research domains."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import (
    ActionLevel,
    BarSpan,
    DataSource,
    EvalDomain,
    EvalErrorType,
    InstrumentType,
    JournalEventType,
    Market,
    MarketRegime,
    PlanOutcomeStatus,
    SignalDirection,
    ThemeStance,
    WatchStatus,
)
from .serialization import parse_enum, to_plain


class Serializable:
    """Mixin for dataclasses that need dict serialization."""

    def to_dict(self) -> dict[str, Any]:
        return to_plain(self)


@dataclass(slots=True)
class Instrument(Serializable):
    symbol: str
    name: str = ""
    instrument_type: InstrumentType = InstrumentType.STOCK
    market: Market = Market.UNKNOWN
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Instrument":
        return cls(
            symbol=str(data.get("symbol", "")),
            name=str(data.get("name", "")),
            instrument_type=parse_enum(InstrumentType, data.get("instrument_type"), InstrumentType.STOCK),
            market=parse_enum(Market, data.get("market"), Market.UNKNOWN),
            raw=dict(data.get("raw") or {}),
        )


@dataclass(slots=True)
class Bar(Serializable):
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    amount: float = 0.0
    span: BarSpan = BarSpan.DAY1
    source: DataSource = DataSource.UNKNOWN
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Bar":
        return cls(
            symbol=str(data.get("symbol", "")),
            timestamp=str(data.get("timestamp", "")),
            open=float(data.get("open", 0.0)),
            high=float(data.get("high", 0.0)),
            low=float(data.get("low", 0.0)),
            close=float(data.get("close", 0.0)),
            volume=float(data.get("volume", 0.0)),
            amount=float(data.get("amount", 0.0)),
            span=parse_enum(BarSpan, data.get("span"), BarSpan.DAY1),
            source=parse_enum(DataSource, data.get("source"), DataSource.UNKNOWN),
            raw=dict(data.get("raw") or {}),
        )


@dataclass(slots=True)
class QuoteSnapshot(Serializable):
    symbol: str
    trade_date: str
    price: float
    pct_chg: float = 0.0
    turnover: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    source: DataSource = DataSource.UNKNOWN
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketBreadth(Serializable):
    trade_date: str
    turnover: float = 0.0
    advancers: int = 0
    decliners: int = 0
    flat_count: int = 0
    limit_up_count: int = 0
    failed_limit_up_count: int = 0
    limit_down_count: int = 0
    seal_rate: float = 0.0
    failed_limit_up_rate: float = 0.0
    source: DataSource = DataSource.UNKNOWN
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IndexEnvironment(Serializable):
    trade_date: str
    name: str
    symbol: str = ""
    pct_chg: float = 0.0
    five_day_pct: float = 0.0
    shape: str = ""
    environment: str = ""
    role: str = ""
    meaning: str = ""
    source: DataSource = DataSource.UNKNOWN
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketRegimeResult(Serializable):
    trade_date: str
    regime: MarketRegime = MarketRegime.UNKNOWN
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ThemeScore(Serializable):
    trade_date: str
    theme: str
    total_score: float = 0.0
    stance: ThemeStance = ThemeStance.UNKNOWN
    flow_score: float = 0.0
    map_score: float = 0.0
    core_score: float = 0.0
    timing_score: float = 0.0
    core_names: list[str] = field(default_factory=list)
    confirm_signal: str = ""
    give_up_signal: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StockSignal(Serializable):
    trade_date: str
    symbol: str
    name: str = ""
    signal_name: str = ""
    direction: SignalDirection = SignalDirection.UNKNOWN
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    key_levels: dict[str, float] = field(default_factory=dict)
    invalidation: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TomorrowPlanItem(Serializable):
    theme: str
    priority: int
    action: ActionLevel = ActionLevel.UNKNOWN
    candidates: list[str] = field(default_factory=list)
    confirm_signal: str = ""
    give_up_signal: str = ""
    position_constraint: str = ""
    reasons: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PerspectiveAnalysis(Serializable):
    source: str
    focus: str = ""
    summary: str = ""
    supports: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TomorrowPlan(Serializable):
    trade_date: str
    generated_at: str = ""
    market_regime: MarketRegime = MarketRegime.UNKNOWN
    summary: str = ""
    items: list[TomorrowPlanItem] = field(default_factory=list)
    data_limits: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DailyReview(Serializable):
    trade_date: str
    summary: str = ""
    market_regime: MarketRegime = MarketRegime.UNKNOWN
    findings: list[str] = field(default_factory=list)
    tomorrow_plan: TomorrowPlan | None = None
    data_limits: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WatchItem(Serializable):
    item_id: str
    item_type: InstrumentType
    symbol: str = ""
    name: str = ""
    theme: str = ""
    horizon: str = ""
    status: WatchStatus = WatchStatus.CANDIDATE
    trigger: str = ""
    invalidation: str = ""
    next_check_date: str = ""
    source_plan_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PlanOutcome(Serializable):
    plan_id: str
    trade_date: str
    status: PlanOutcomeStatus = PlanOutcomeStatus.PENDING
    triggered_items: list[str] = field(default_factory=list)
    invalidated_items: list[str] = field(default_factory=list)
    notes: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DecisionJournalEntry(Serializable):
    entry_id: str
    event_type: JournalEventType
    trade_date: str
    created_at: str
    title: str = ""
    summary: str = ""
    related_id: str = ""
    score: float | None = None
    error_types: list[EvalErrorType] = field(default_factory=list)
    suggested_fix: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BacktestConfig(Serializable):
    strategy_name: str
    start_date: str
    end_date: str
    universe: list[str] = field(default_factory=list)
    initial_cash: float = 1_000_000.0
    commission_rate: float = 0.0003
    slippage_rate: float = 0.001
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SignalEvent(Serializable):
    trade_date: str
    symbol: str
    direction: SignalDirection
    score: float = 0.0
    price: float | None = None
    size: float | None = None
    reason: str = ""
    source: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TradeRecord(Serializable):
    trade_id: str
    symbol: str
    entry_date: str
    exit_date: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    pnl: float = 0.0
    return_pct: float = 0.0
    fees: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EquityPoint(Serializable):
    trade_date: str
    equity: float
    cash: float = 0.0
    exposure: float = 0.0
    drawdown: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PerformanceReport(Serializable):
    strategy_name: str
    start_date: str
    end_date: str
    total_return: float = 0.0
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_loss_ratio: float = 0.0
    trade_count: int = 0
    exposure_days: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BacktestResult(Serializable):
    config: BacktestConfig
    performance: PerformanceReport
    trades: list[TradeRecord] = field(default_factory=list)
    equity_curve: list[EquityPoint] = field(default_factory=list)
    signals: list[SignalEvent] = field(default_factory=list)
    data_limits: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalSample(Serializable):
    sample_id: str
    domain: EvalDomain
    input_data: dict[str, Any]
    ground_truth: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalResult(Serializable):
    sample_id: str
    domain: EvalDomain
    target_version: str = ""
    judge_version: str = ""
    format_ok: bool = True
    field_complete: bool = True
    score: float = 0.0
    passed: bool = False
    error_types: list[EvalErrorType] = field(default_factory=list)
    evidence_quality: float = 0.0
    actionability: float = 0.0
    risk_control: float = 0.0
    notes: str = ""
    suggested_fix: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalReport(Serializable):
    domain: EvalDomain
    target_version: str = ""
    judge_version: str = ""
    total: int = 0
    passed: int = 0
    avg_score: float = 0.0
    error_counts: dict[str, int] = field(default_factory=dict)
    results: list[EvalResult] = field(default_factory=list)
