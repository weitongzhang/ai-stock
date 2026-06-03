#!/usr/bin/env python3
"""
FTShare-market-data 全量子 skill 测试运行器。

功能：
  1. 顺序执行所有子 skill 测试用例
  2. 每个接口返回的 JSON 单独输出到 test_logs/<subskill>_<timestamp>.json
  3. 汇总测试结果到 test_logs/summary_<timestamp>.txt
  4. 支持按关键词过滤用例

用法：
    python3 test_runner.py                  # 运行全部测试
    python3 test_runner.py stock            # 只跑股票相关
    python3 test_runner.py etf fund         # 跑 ETF 和基金
    python3 test_runner.py --clean          # 清空历史日志后运行
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

# 脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()
RUN_PY = SCRIPT_DIR / "run.py"
LOG_DIR = SCRIPT_DIR / "test_logs"

# 每个子 skill 请求的超时时间（秒）
REQUEST_TIMEOUT_SEC = 30

# 颜色输出（仅 TTY 生效）
_USE_COLOR = sys.stdout.isatty()
_GREEN = "\033[92m" if _USE_COLOR else ""
_RED = "\033[91m" if _USE_COLOR else ""
_YELLOW = "\033[93m" if _USE_COLOR else ""
_CYAN = "\033[96m" if _USE_COLOR else ""
_RESET = "\033[0m" if _USE_COLOR else ""


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    """一条测试用例的定义。"""

    name: str
    """人类可读的测试名称"""

    subskill: str
    """子 skill 名称"""

    args: List[str]
    """传给 handler 的命令行参数列表"""

    key_checks: List[str] = field(default_factory=list)
    """期望响应 JSON 中存在的 key 列表"""

    custom_validator: Optional[Callable[[object], Optional[str]]] = None
    """可选的额外校验函数"""

    skip: bool = False
    """标记为 True 则跳过此用例"""

    skip_reason: str = ""
    """跳过原因说明"""


@dataclass
class TestResult:
    """单条测试的执行结果。"""

    case: TestCase
    passed: bool
    error_msg: str = ""
    elapsed_ms: int = 0
    log_file: str = ""  # 日志文件路径（相对于 test_logs/）
    json_size: int = 0  # JSON 字节数


# ---------------------------------------------------------------------------
# 公共校验辅助函数
# ---------------------------------------------------------------------------

def _check_keys(data: object, keys: List[str]) -> Optional[str]:
    """
    递归检查 data 中是否存在 keys 中的每个 key。
    返回 None 表示全部通过，返回错误描述字符串表示失败。
    """
    if not keys:
        return None

    if isinstance(data, list):
        if len(data) == 0:
            return None
        target = data[0]
    elif isinstance(data, dict):
        target = data
    else:
        return f"响应根类型异常：{type(data)}"

    missing = [k for k in keys if k not in target]
    if missing:
        return f"响应缺少字段：{missing}"
    return None


def _require_list_or_items(data: object) -> Optional[str]:
    """校验响应为列表，或字典中含 items 列表字段。"""
    if isinstance(data, list):
        return None
    if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        return None
    return "响应既不是列表，也不含 items 字段"


def _require_non_empty(data: object) -> Optional[str]:
    """校验响应为非空列表，或字典中含非空 items 字段。"""
    if isinstance(data, list):
        if len(data) == 0:
            return "响应列表为空，预期有数据"
        return None
    if isinstance(data, dict):
        items = data.get("items", [])
        if isinstance(items, list) and len(items) == 0:
            return None
    return None


# ---------------------------------------------------------------------------
# 所有测试用例定义
# ---------------------------------------------------------------------------

def _build_test_cases() -> List[TestCase]:
    """构建并返回全部测试用例列表。"""

    cases: List[TestCase] = []

    # -----------------------------------------------------------------------
    # 工具类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="get-nth-trade-date - 前5个交易日",
        subskill="get-nth-trade-date",
        args=["--n", "5"],
        key_checks=["n", "current_date", "nth_trade_date"],
    ))

    # -----------------------------------------------------------------------
    # 股票行情类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="stock-list-all-stocks - 全量股票列表",
        subskill="stock-list-all-stocks",
        args=[],
        custom_validator=lambda d: _require_non_empty(d),
    ))

    cases.append(TestCase(
        name="stock-quotes-list - 按涨跌幅降序首页",
        subskill="stock-quotes-list",
        args=["--order_by", "change_rate desc", "--page_no", "1", "--page_size", "10"],
        key_checks=["total_size", "stocks"],
    ))

    cases.append(TestCase(
        name="stock-security-info - 贵州茅台基本信息",
        subskill="stock-security-info",
        args=["--symbol", "600519.SH"],
        key_checks=["symbol", "symbol_name", "change_rate", "market_cap"],
    ))

    cases.append(TestCase(
        name="stock-ohlcs - 平安银行日线K线20根",
        subskill="stock-ohlcs",
        args=["--stock", "000001.SZ", "--span", "DAY1", "--limit", "20"],
        key_checks=["ohlcs"],
    ))

    cases.append(TestCase(
        name="stock-ohlcs - 科创板周线K线",
        subskill="stock-ohlcs",
        args=["--stock", "688295.XSHG", "--span", "WEEK1", "--limit", "10"],
        key_checks=["ohlcs"],
    ))

    cases.append(TestCase(
        name="stock-prices - 平安银行今日分时",
        subskill="stock-prices",
        args=["--stock", "000001.SZ", "--since", "TODAY"],
        key_checks=["prices"],
    ))

    cases.append(TestCase(
        name="stock-ipos - IPO列表首页",
        subskill="stock-ipos",
        args=["--page", "1", "--page_size", "10"],
        key_checks=["items"],
    ))

    # -----------------------------------------------------------------------
    # 股东持仓类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="stock-holder-ten - 万科十大股东",
        subskill="stock-holder-ten",
        args=["--stock_code", "000002.SZ"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-holder-ften - 万科十大流通股东",
        subskill="stock-holder-ften",
        args=["--stock_code", "000002.SZ"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-holder-nums - 平安银行股东人数",
        subskill="stock-holder-nums",
        args=["--stock_code", "000001.SZ"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-share-chg - 平安银行增减持",
        subskill="stock-share-chg",
        args=["--stock_code", "000001.SZ", "--page", "1", "--page_size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    # -----------------------------------------------------------------------
    # 财务报表类 - 单股所有报告期
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="stock-income-single-stock-all-periods - 贵州茅台利润表",
        subskill="stock-income-single-stock-all-periods",
        args=["--stock-code", "600519.SH"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-balance-single-stock-all-periods - 贵州茅台资产负债表",
        subskill="stock-balance-single-stock-all-periods",
        args=["--stock-code", "600519.SH"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-cashflow-single-stock-all-periods - 贵州茅台现金流量表",
        subskill="stock-cashflow-single-stock-all-periods",
        args=["--stock-code", "600519.SH"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-performance-express-single-stock-all-periods - 贵州茅台业绩快报",
        subskill="stock-performance-express-single-stock-all-periods",
        args=["--stock-code", "600519.SH", "--page", "1", "--page-size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="stock-performance-forecast-single-stock-all-periods - 贵州茅台业绩预告",
        subskill="stock-performance-forecast-single-stock-all-periods",
        args=["--stock-code", "600519.SH", "--page", "1", "--page-size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    # -----------------------------------------------------------------------
    # 财务报表类 - 全市场特定报告期
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="stock-income-all-stocks-specific-period - 2024年年报利润表首页",
        subskill="stock-income-all-stocks-specific-period",
        args=["--year", "2024", "--report-type", "annual", "--page", "1", "--page-size", "10"],
        key_checks=["items"],
    ))

    cases.append(TestCase(
        name="stock-balance-all-stocks-specific-period - 2024年年报资产负债表首页",
        subskill="stock-balance-all-stocks-specific-period",
        args=["--year", "2024", "--report-type", "annual", "--page", "1", "--page-size", "10"],
        key_checks=["items"],
    ))

    cases.append(TestCase(
        name="stock-cashflow-all-stocks-specific-period - 2024年年报现金流首页",
        subskill="stock-cashflow-all-stocks-specific-period",
        args=["--year", "2024", "--report-type", "annual", "--page", "1", "--page-size", "10"],
        key_checks=["items"],
    ))

    cases.append(TestCase(
        name="stock-performance-express-all-stocks-specific-period - 2024年年报业绩快报首页",
        subskill="stock-performance-express-all-stocks-specific-period",
        args=["--year", "2024", "--report-type", "annual", "--page", "1", "--page-size", "10"],
        key_checks=["items"],
    ))

    cases.append(TestCase(
        name="stock-performance-forecast-all-stocks-specific-period - 2025年一季报业绩预告首页",
        subskill="stock-performance-forecast-all-stocks-specific-period",
        args=["--year", "2025", "--report-type", "q1", "--page", "1", "--page-size", "10"],
        key_checks=["items"],
    ))

    # -----------------------------------------------------------------------
    # 大宗交易 / 两融 / 质押
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="block-trades - 大宗交易列表",
        subskill="block-trades",
        args=[],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="margin-trading-details - 融资融券明细首页",
        subskill="margin-trading-details",
        args=["--page", "1", "--page_size", "10"],
        key_checks=["items"],
    ))

    cases.append(TestCase(
        name="pledge-summary - 全市场质押总揽",
        subskill="pledge-summary",
        args=[],
        custom_validator=lambda d: _require_non_empty(d),
    ))

    cases.append(TestCase(
        name="pledge-detail - 平安银行质押明细首页",
        subskill="pledge-detail",
        args=["--stock_code", "000001.SZ", "--page", "1", "--page_size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    # -----------------------------------------------------------------------
    # 新闻语义搜索
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="semantic-search-news - 搜索人工智能",
        subskill="semantic-search-news",
        args=["--query", "人工智能", "--limit", "5"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="semantic-search-news - 搜索美联储降息",
        subskill="semantic-search-news",
        args=["--query", "美联储降息", "--limit", "3"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    # -----------------------------------------------------------------------
    # 可转债类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="cb-lists - 可转债列表",
        subskill="cb-lists",
        args=[],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="cb-base-data - 110070.SH 可转债基础信息",
        subskill="cb-base-data",
        args=["--symbol_code", "110070.SH"],
        custom_validator=lambda d: (
            None if isinstance(d, dict) and len(d) > 0
            else "响应为空字典或非字典类型"
        ),
    ))

    # -----------------------------------------------------------------------
    # ETF 类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="etf-detail - 510050上证50ETF详情",
        subskill="etf-detail",
        args=["--etf", "510050.XSHG"],
        custom_validator=lambda d: (
            None if isinstance(d, dict) and len(d) > 0
            else "响应为空字典或非字典类型"
        ),
    ))

    cases.append(TestCase(
        name="etf-list-paginated - ETF列表按涨跌幅降序",
        subskill="etf-list-paginated",
        args=["--order_by", "change_rate desc", "--page_size", "10", "--page_no", "1"],
        key_checks=["total_size", "etfs"],
    ))

    cases.append(TestCase(
        name="etf-ohlcs - 510050日线K线20根",
        subskill="etf-ohlcs",
        args=["--etf", "510050.XSHG", "--span", "DAY1", "--limit", "20"],
        key_checks=["ohlcs"],
    ))

    cases.append(TestCase(
        name="etf-prices - 510050今日分时",
        subskill="etf-prices",
        args=["--etf", "510050.XSHG", "--since", "TODAY"],
        key_checks=["prices"],
    ))

    cases.append(TestCase(
        name="etf-component - 510300沪深300ETF成份股",
        subskill="etf-component",
        args=["--symbol", "510300.XSHG"],
        key_checks=["symbol", "components"],
    ))

    cases.append(TestCase(
        name="etf-pre-single - 510300盘前数据",
        subskill="etf-pre-single",
        args=["--symbol", "510300.XSHG"],
        custom_validator=lambda d: (
            None if isinstance(d, dict) and len(d) > 0
            else "响应为空字典或非字典类型"
        ),
        skip=True,
        skip_reason="盘前数据接口在非交易时段返回系统错误，需在交易日盘前时段运行",
    ))

    cases.append(TestCase(
        name="etf-pcfs - 指定日期PCF文件列表",
        subskill="etf-pcfs",
        args=["--date", "20260314"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="etf-pcf-download - 下载PCF文件（需真实filename，跳过）",
        subskill="etf-pcf-download",
        args=["--filename", "pcf_159003_20260314.xml"],
        skip=True,
        skip_reason="依赖真实 PCF filename，需先调 etf-pcfs 确认文件是否存在",
    ))

    # -----------------------------------------------------------------------
    # 指数类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="index-detail - 000001上证指数详情",
        subskill="index-detail",
        args=["--index", "000001.XSHG"],
        custom_validator=lambda d: (
            None if isinstance(d, dict) and len(d) > 0
            else "响应为空字典或非字典类型"
        ),
    ))

    cases.append(TestCase(
        name="index-list-paginated - 指数列表首页",
        subskill="index-list-paginated",
        args=["--page_size", "10", "--page_no", "1"],
        key_checks=["total_size", "indices"],
    ))

    cases.append(TestCase(
        name="index-ohlcs - 沪深300日线K线20根",
        subskill="index-ohlcs",
        args=["--index", "000300.XSHG", "--span", "DAY1", "--limit", "20"],
        key_checks=["ohlcs"],
    ))

    cases.append(TestCase(
        name="index-prices - 上证指数今日分时",
        subskill="index-prices",
        args=["--index", "000001.XSHG", "--since", "TODAY"],
        key_checks=["prices"],
    ))

    # -----------------------------------------------------------------------
    # 基金类
    # -----------------------------------------------------------------------

    cases.append(TestCase(
        name="fund-basicinfo-single-fund - 000001基金基础信息",
        subskill="fund-basicinfo-single-fund",
        args=["--institution-code", "000001"],
        custom_validator=lambda d: (
            None if isinstance(d, dict) and len(d) > 0
            else "响应为空字典或非字典类型"
        ),
    ))

    cases.append(TestCase(
        name="fund-cal-return-single-fund-specific-period - 159619近一年收益",
        subskill="fund-cal-return-single-fund-specific-period",
        args=["--institution-code", "159619", "--cal-type", "1Y"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="fund-nav-single-fund-paginated - 000001净值历史首页",
        subskill="fund-nav-single-fund-paginated",
        args=["--institution-code", "000001", "--page", "1", "--page-size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="fund-overview-all-funds-paginated - 基金概览首页",
        subskill="fund-overview-all-funds-paginated",
        args=["--page", "1", "--page-size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    cases.append(TestCase(
        name="fund-support-symbols-all-funds-paginated - 基金支持标的首页",
        subskill="fund-support-symbols-all-funds-paginated",
        args=["--page", "1", "--page-size", "10"],
        custom_validator=lambda d: _require_list_or_items(d),
    ))

    # -----------------------------------------------------------------------
    # 宏观经济 - 中国
    # -----------------------------------------------------------------------

    _china_economic_no_arg = [
        ("economic-china-cpi-monthly",                   "中国CPI月度数据"),
        ("economic-china-ppi-monthly",                   "中国PPI月度数据"),
        ("economic-china-pmi-monthly",                   "中国PMI月度数据"),
        ("economic-china-gdp-quarterly",                 "中国GDP季度数据"),
        ("economic-china-lpr-monthly",                   "中国LPR月度数据"),
        ("economic-china-money-supply-monthly",          "中国货币供应M2月度数据"),
        ("economic-china-credit-loans-monthly",          "中国社会融资规模月度数据"),
        ("economic-china-retail-sales-monthly",          "中国社会消费品零售总额月度"),
        ("economic-china-customs-trade-monthly",         "中国海关进出口月度数据"),
        ("economic-china-industrial-added-value-monthly","中国工业增加值月度数据"),
        ("economic-china-fixed-asset-investment-monthly","中国固定资产投资月度数据"),
        ("economic-china-fiscal-revenue-monthly",        "中国财政收入月度数据"),
        ("economic-china-tax-revenue-monthly",           "中国税收收入月度数据"),
        ("economic-china-forex-gold-monthly",            "中国外汇黄金储备月度数据"),
        ("economic-china-reserve-ratio-monthly",         "中国存款准备金率月度数据"),
    ]
    for subskill, label in _china_economic_no_arg:
        cases.append(TestCase(
            name=f"{subskill} - {label}",
            subskill=subskill,
            args=[],
            custom_validator=lambda d: _require_list_or_items(d),
        ))

    # -----------------------------------------------------------------------
    # 宏观经济 - 美国
    # -----------------------------------------------------------------------

    _us_types = [
        "ism-manufacturing",
        "nonfarm-payroll",
        "cpi-mom",
        "cpi-yoy",
        "fed-funds-rate-upper",
        "unemployment-rate",
    ]
    for us_type in _us_types:
        cases.append(TestCase(
            name=f"economic-us-economic-by-type - {us_type}",
            subskill="economic-us-economic-by-type",
            args=["--type", us_type],
            custom_validator=lambda d: _require_list_or_items(d),
        ))

    return cases


# ---------------------------------------------------------------------------
# 测试执行引擎
# ---------------------------------------------------------------------------

def _run_single(case: TestCase, run_timestamp: str) -> TestResult:
    """
    执行一条测试用例并返回结果。
    成功时将响应 JSON 写入 test_logs/<subskill>_<timestamp>.json。
    """
    cmd = [sys.executable, str(RUN_PY), case.subskill] + case.args

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=REQUEST_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        elapsed = int((time.monotonic() - t0) * 1000)
        return TestResult(
            case=case,
            passed=False,
            error_msg=f"超时（>{REQUEST_TIMEOUT_SEC}s）",
            elapsed_ms=elapsed,
        )
    except Exception as exc:
        elapsed = int((time.monotonic() - t0) * 1000)
        return TestResult(
            case=case,
            passed=False,
            error_msg=f"subprocess 异常：{exc}",
            elapsed_ms=elapsed,
        )

    elapsed = int((time.monotonic() - t0) * 1000)

    # 1. 检查退出码
    if proc.returncode != 0:
        stderr_snippet = proc.stderr.strip()[:300]
        return TestResult(
            case=case,
            passed=False,
            error_msg=f"退出码 {proc.returncode}，stderr：{stderr_snippet}",
            elapsed_ms=elapsed,
        )

    # 2. 检查 stdout 为合法 JSON
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        snippet = proc.stdout.strip()[:200]
        return TestResult(
            case=case,
            passed=False,
            error_msg=f"JSON 解析失败：{exc}，输出片段：{snippet}",
            elapsed_ms=elapsed,
        )

    # 3. key_checks 字段存在性校验
    key_err = _check_keys(data, case.key_checks)
    if key_err:
        return TestResult(
            case=case,
            passed=False,
            error_msg=key_err,
            elapsed_ms=elapsed,
        )

    # 4. 自定义校验
    if case.custom_validator:
        custom_err = case.custom_validator(data)
        if custom_err:
            return TestResult(
                case=case,
                passed=False,
                error_msg=custom_err,
                elapsed_ms=elapsed,
            )

    # 通过：写日志文件
    log_filename = f"{case.subskill}_{run_timestamp}.json"
    log_path = LOG_DIR / log_filename
    try:
        log_path.write_text(proc.stdout, encoding="utf-8")
        json_size = len(proc.stdout.encode("utf-8"))
    except Exception as e:
        return TestResult(
            case=case,
            passed=False,
            error_msg=f"写日志文件失败：{e}",
            elapsed_ms=elapsed,
        )

    return TestResult(
        case=case,
        passed=True,
        elapsed_ms=elapsed,
        log_file=log_filename,
        json_size=json_size,
    )


def _make_summary_line(data: object) -> str:
    """生成响应数据的简短摘要（单行）。"""
    if isinstance(data, list):
        return f"[list] 条数={len(data)}"
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            total = data.get("total_items") or data.get("total") or "?"
            return f"[dict] items={len(items)}, total={total}"
        keys_preview = list(data.keys())[:6]
        return f"[dict] keys={keys_preview}"
    return f"[{type(data).__name__}]"


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> None:
    """解析命令行参数，过滤用例，顺序执行并汇报结果。"""
    args = sys.argv[1:]

    # --clean：清空历史日志
    clean = "--clean" in args
    if clean:
        args = [a for a in args if a != "--clean"]

    # 剩余参数作为名称过滤关键词
    filters = [a.lower() for a in args]

    # 创建日志目录
    LOG_DIR.mkdir(exist_ok=True)

    if clean:
        print(f"{_YELLOW}清空历史日志：{LOG_DIR}{_RESET}")
        for f in LOG_DIR.glob("*.json"):
            f.unlink()
        for f in LOG_DIR.glob("summary_*.txt"):
            f.unlink()

    # 生成本次运行时间戳（用于日志文件名）
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_cases = _build_test_cases()

    # 按过滤词筛选
    if filters:
        filtered = [
            c for c in all_cases
            if any(f in c.name.lower() or f in c.subskill.lower() for f in filters)
        ]
    else:
        filtered = all_cases

    total = len(filtered)
    skipped = sum(1 for c in filtered if c.skip)
    to_run = [c for c in filtered if not c.skip]

    print(f"\n{'='*70}")
    print(f"FTShare-market-data 子 skill 集成测试")
    print(f"用例总数: {total}  跳过: {skipped}  执行: {len(to_run)}")
    print(f"日志目录: {LOG_DIR}")
    print(f"{'='*70}\n")

    results: List[TestResult] = []

    for i, case in enumerate(filtered, 1):
        prefix = f"[{i:>3}/{total}]"

        if case.skip:
            print(f"{prefix} {_YELLOW}SKIP{_RESET}  {case.name}")
            if case.skip_reason:
                print(f"         原因：{case.skip_reason}")
            results.append(TestResult(case=case, passed=True))
            continue

        # 执行测试
        result = _run_single(case, run_timestamp)
        results.append(result)

        status = f"{_GREEN}PASS{_RESET}" if result.passed else f"{_RED}FAIL{_RESET}"
        timing = f"{result.elapsed_ms}ms"
        print(f"{prefix} {status}  {case.name}  ({timing})")

        if result.passed and result.log_file:
            size_kb = result.json_size / 1024
            print(f"         {_CYAN}日志：test_logs/{result.log_file}  ({size_kb:.1f} KB){_RESET}")

        if not result.passed:
            print(f"         {_RED}错误：{result.error_msg}{_RESET}")

    # -----------------------------------------------------------------------
    # 汇总报告
    # -----------------------------------------------------------------------
    run_results = [r for r in results if not r.case.skip]
    passed_count = sum(1 for r in run_results if r.passed)
    failed_count = sum(1 for r in run_results if not r.passed)
    total_elapsed = sum(r.elapsed_ms for r in run_results)

    print(f"\n{'='*70}")
    print(f"结果汇总：PASS={passed_count}  FAIL={failed_count}  SKIP={skipped}")
    print(f"总耗时：{total_elapsed / 1000:.1f}s")

    # 写汇总日志
    summary_file = LOG_DIR / f"summary_{run_timestamp}.txt"
    with summary_file.open("w", encoding="utf-8") as f:
        f.write(f"FTShare-market-data 测试汇总\n")
        f.write(f"运行时间: {run_timestamp}\n")
        f.write(f"用例总数: {total}  跳过: {skipped}  执行: {len(to_run)}\n")
        f.write(f"PASS={passed_count}  FAIL={failed_count}\n")
        f.write(f"总耗时: {total_elapsed / 1000:.1f}s\n\n")

        if failed_count > 0:
            f.write("失败用例列表：\n")
            for r in run_results:
                if not r.passed:
                    f.write(f"  - {r.case.name}\n")
                    f.write(f"    {r.error_msg}\n")
            f.write("\n")

        f.write("全部用例明细：\n")
        for i, r in enumerate(results, 1):
            status = "SKIP" if r.case.skip else ("PASS" if r.passed else "FAIL")
            f.write(f"  [{i:>3}] {status:4s}  {r.case.name}  ({r.elapsed_ms}ms)\n")
            if r.log_file:
                f.write(f"        日志：{r.log_file}\n")
            if not r.passed and r.error_msg:
                f.write(f"        错误：{r.error_msg}\n")

    print(f"{_CYAN}汇总日志：test_logs/{summary_file.name}{_RESET}")

    if failed_count > 0:
        print(f"\n{_RED}失败用例列表：{_RESET}")
        for r in run_results:
            if not r.passed:
                print(f"  - {r.case.name}")
                print(f"    {r.error_msg}")

    print(f"{'='*70}\n")

    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
