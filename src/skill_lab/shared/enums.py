"""Shared enum definitions for the trading research system."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Small compatibility base for string-valued enums."""

    def __str__(self) -> str:
        return self.value


class InstrumentType(StrEnum):
    STOCK = "stock"
    INDEX = "index"
    ETF = "etf"
    CONVERTIBLE_BOND = "convertible_bond"
    FUND = "fund"
    THEME = "theme"
    SECTOR = "sector"


class Market(StrEnum):
    SH = "SH"
    SZ = "SZ"
    BJ = "BJ"
    HK = "HK"
    US = "US"
    UNKNOWN = "UNKNOWN"


class BarSpan(StrEnum):
    MIN1 = "1m"
    MIN5 = "5m"
    MIN15 = "15m"
    MIN30 = "30m"
    MIN60 = "60m"
    DAY1 = "1d"
    WEEK1 = "1w"
    MONTH1 = "1mo"
    YEAR1 = "1y"


class DataSource(StrEnum):
    FTSHARE = "ftshare"
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    FILE = "file"
    SAMPLE = "sample"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class MarketRegime(StrEnum):
    ATTACK = "attack"
    STRUCTURAL_REPAIR = "structural_repair"
    CHOPPY_TRIAL = "choppy_trial"
    DEFENSIVE = "defensive"
    UNKNOWN = "unknown"


class ThemeStance(StrEnum):
    ATTACK = "attack"
    ACTIVE_WATCH = "active_watch"
    TRACK_WAIT = "track_wait"
    GIVE_UP = "give_up"
    UNKNOWN = "unknown"


class ThemeLeaderRole(StrEnum):
    FRONT_ROW = "front_row"
    CAPACITY_CORE = "capacity_core"
    FOLLOWER = "follower"
    RISK_SAMPLE = "risk_sample"
    UNKNOWN = "unknown"


class ActionLevel(StrEnum):
    MAIN_ATTACK = "main_attack"
    CORE_DIP = "core_dip"
    WATCH = "watch"
    OBSERVE_ONLY = "observe_only"
    GIVE_UP = "give_up"
    UNKNOWN = "unknown"


class SignalDirection(StrEnum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    WAIT = "wait"
    AVOID = "avoid"
    UNKNOWN = "unknown"


class WatchStatus(StrEnum):
    CANDIDATE = "candidate"
    WATCHING = "watching"
    TRIGGERED = "triggered"
    INVALIDATED = "invalidated"
    REVIEWING = "reviewing"
    CLOSED = "closed"


class PlanOutcomeStatus(StrEnum):
    PENDING = "pending"
    TRIGGERED = "triggered"
    NOT_TRIGGERED = "not_triggered"
    INVALIDATED = "invalidated"
    SUCCESS = "success"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class JournalEventType(StrEnum):
    PLAN_CREATED = "plan_created"
    PLAN_EVALUATED = "plan_evaluated"
    PLAN_OUTCOME = "plan_outcome"
    DAILY_REVIEW_CREATED = "daily_review_created"
    DAILY_REVIEW_EVALUATED = "daily_review_evaluated"
    RULE_UPDATE = "rule_update"
    BACKTEST_REVIEW = "backtest_review"


class EvalDomain(StrEnum):
    DATA = "data"
    MARKET_REGIME = "market_regime"
    THEME_STRENGTH = "theme_strength"
    LIFT_LEADER = "lift_leader"
    BSA_SIGNAL = "bsa_signal"
    YC_BUY_SIGNAL = "yc_buy_signal"
    TOMORROW_PLAN = "tomorrow_plan"
    DAILY_REVIEW = "daily_review"
    WATCHLIST = "watchlist"
    BACKTEST = "backtest"


class EvalErrorType(StrEnum):
    FORMAT_ERROR = "FORMAT_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    DATA_ERROR = "DATA_ERROR"
    WRONG_REGIME = "WRONG_REGIME"
    WRONG_THEME = "WRONG_THEME"
    WRONG_LEADER = "WRONG_LEADER"
    WRONG_STRUCTURE = "WRONG_STRUCTURE"
    FALSE_BREAKOUT_MISS = "FALSE_BREAKOUT_MISS"
    BAD_ACTION = "BAD_ACTION"
    BAD_INVALIDATION = "BAD_INVALIDATION"
    OVERCONFIDENT = "OVERCONFIDENT"
    NO_EVIDENCE = "NO_EVIDENCE"
    BACKTEST_MISMATCH = "BACKTEST_MISMATCH"
