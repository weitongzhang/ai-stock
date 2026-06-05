"""Data quality checks for normalized market data objects."""

from __future__ import annotations

from dataclasses import dataclass, field

from skill_lab.shared.schemas import Bar, IndexEnvironment, MarketBreadth, ThemeScore


@dataclass(slots=True)
class DataQualityIssue:
    severity: str
    code: str
    message: str
    field: str = ""
    item_id: str = ""


@dataclass(slots=True)
class DataQualityReport:
    subject: str
    checked_count: int = 0
    issues: list[DataQualityIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(self, severity: str, code: str, message: str, field: str = "", item_id: str = "") -> None:
        self.issues.append(
            DataQualityIssue(
                severity=severity,
                code=code,
                message=message,
                field=field,
                item_id=item_id,
            )
        )


@dataclass(slots=True)
class QualityBaseline:
    min_theme_rows: int = 3
    min_index_rows: int = 3
    min_bar_rows: int = 30
    max_limit_up_count: int = 300
    max_limit_down_count: int = 300
    max_failed_limit_up_count: int = 300


DEFAULT_BASELINE = QualityBaseline()


def check_market_breadth(
    breadth: MarketBreadth,
    baseline: QualityBaseline = DEFAULT_BASELINE,
) -> DataQualityReport:
    report = DataQualityReport(subject=f"market_breadth:{breadth.trade_date}", checked_count=1)
    if not breadth.trade_date:
        report.add("error", "missing_trade_date", "market breadth trade_date is missing", "trade_date")
    for field_name in ("advancers", "decliners", "limit_up_count", "limit_down_count"):
        value = getattr(breadth, field_name)
        if value < 0:
            report.add("error", "negative_count", f"{field_name} cannot be negative", field_name)
    for field_name in ("seal_rate", "failed_limit_up_rate"):
        value = getattr(breadth, field_name)
        if value < 0 or value > 100:
            report.add("warning", "rate_out_of_range", f"{field_name} should be within 0-100", field_name)
    if breadth.limit_up_count > baseline.max_limit_up_count:
        report.add("warning", "limit_up_count_outlier", "limit_up_count is above baseline range", "limit_up_count")
    if breadth.limit_down_count > baseline.max_limit_down_count:
        report.add("warning", "limit_down_count_outlier", "limit_down_count is above baseline range", "limit_down_count")
    if breadth.failed_limit_up_count > baseline.max_failed_limit_up_count:
        report.add("warning", "failed_limit_up_count_outlier", "failed_limit_up_count is above baseline range", "failed_limit_up_count")
    if breadth.advancers == 0 and breadth.decliners == 0:
        report.add("warning", "missing_breadth_counts", "advancers and decliners are both zero")
    return report


def check_index_environment(
    rows: list[IndexEnvironment],
    trade_date: str = "",
    baseline: QualityBaseline = DEFAULT_BASELINE,
) -> DataQualityReport:
    report = DataQualityReport(subject=f"index_environment:{trade_date}", checked_count=len(rows))
    if not rows:
        report.add("error", "empty_index_environment", "index environment rows are empty")
        return report
    if len(rows) < baseline.min_index_rows:
        report.add("warning", "too_few_index_rows", "index environment row count is below baseline")
    seen: set[str] = set()
    for row in rows:
        item_id = row.symbol or row.name
        if not row.trade_date:
            report.add("error", "missing_trade_date", "index row trade_date is missing", "trade_date", item_id)
        elif trade_date and row.trade_date != trade_date:
            report.add("warning", "date_mismatch", f"index row date {row.trade_date} != {trade_date}", "trade_date", item_id)
        if not row.name:
            report.add("error", "missing_name", "index row name is missing", "name", item_id)
        if item_id in seen:
            report.add("warning", "duplicate_index", f"duplicate index row {item_id}", item_id=item_id)
        seen.add(item_id)
    return report


def check_theme_scores(
    rows: list[ThemeScore],
    trade_date: str = "",
    baseline: QualityBaseline = DEFAULT_BASELINE,
) -> DataQualityReport:
    report = DataQualityReport(subject=f"theme_scores:{trade_date}", checked_count=len(rows))
    if not rows:
        report.add("error", "empty_theme_scores", "theme score rows are empty")
        return report
    if len(rows) < baseline.min_theme_rows:
        report.add("warning", "too_few_theme_rows", "theme score row count is below baseline")
    seen: set[str] = set()
    for row in rows:
        item_id = row.theme
        if not row.theme:
            report.add("error", "missing_theme", "theme name is missing", "theme")
        if trade_date and row.trade_date != trade_date:
            report.add("warning", "date_mismatch", f"theme date {row.trade_date} != {trade_date}", "trade_date", item_id)
        if row.total_score < 0 or row.total_score > 100:
            report.add("warning", "score_out_of_range", "theme total_score should be within 0-100", "total_score", item_id)
        factor_sum = row.flow_score + row.map_score + row.core_score + row.timing_score
        if factor_sum and abs(factor_sum - row.total_score) > 8:
            report.add("warning", "factor_sum_mismatch", "F/M/C/T sum differs from total_score", "total_score", item_id)
        if item_id in seen:
            report.add("warning", "duplicate_theme", f"duplicate theme row {item_id}", item_id=item_id)
        seen.add(item_id)
    return report


def check_bars(
    bars: list[Bar],
    symbol: str = "",
    baseline: QualityBaseline = DEFAULT_BASELINE,
) -> DataQualityReport:
    report = DataQualityReport(subject=f"bars:{symbol}", checked_count=len(bars))
    if not bars:
        report.add("error", "empty_bars", "bar list is empty")
        return report
    if len(bars) < baseline.min_bar_rows:
        report.add("warning", "too_few_bar_rows", "bar row count is below baseline")
    previous_timestamp = ""
    for bar in bars:
        item_id = f"{bar.symbol}:{bar.timestamp}"
        if symbol and bar.symbol != symbol:
            report.add("warning", "symbol_mismatch", f"bar symbol {bar.symbol} != {symbol}", "symbol", item_id)
        if not bar.timestamp:
            report.add("error", "missing_timestamp", "bar timestamp is missing", "timestamp", item_id)
        if previous_timestamp and bar.timestamp < previous_timestamp:
            report.add("warning", "timestamp_not_sorted", "bars should be sorted ascending by timestamp", "timestamp", item_id)
        previous_timestamp = bar.timestamp
        if bar.high < max(bar.open, bar.close) or bar.low > min(bar.open, bar.close):
            report.add("error", "invalid_ohlc", "OHLC values are internally inconsistent", item_id=item_id)
        if min(bar.open, bar.high, bar.low, bar.close) <= 0:
            report.add("warning", "non_positive_price", "bar contains non-positive price", item_id=item_id)
    return report


def merge_reports(subject: str, reports: list[DataQualityReport]) -> DataQualityReport:
    merged = DataQualityReport(subject=subject, checked_count=sum(report.checked_count for report in reports))
    for report in reports:
        merged.issues.extend(report.issues)
    return merged
