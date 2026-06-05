"""Symbol mapping helpers for A-share providers."""

from __future__ import annotations

from skill_lab.shared.enums import Market


def detect_market(symbol: str) -> Market:
    text = symbol.strip().upper()
    if text.endswith((".SH", ".XSHG")):
        return Market.SH
    if text.endswith((".SZ", ".XSHE")):
        return Market.SZ
    if text.endswith((".BJ", ".BJSE")):
        return Market.BJ
    code = text.split(".")[0]
    if code.startswith(("5", "6", "9")):
        return Market.SH
    if code.startswith(("0", "1", "2", "3")):
        return Market.SZ
    if code.startswith(("4", "8")):
        return Market.BJ
    return Market.UNKNOWN


def to_ftshare_stock_symbol(symbol: str) -> str:
    """Convert common A-share symbols to FTShare stock format."""

    code = symbol.strip().upper().split(".")[0]
    market = detect_market(symbol)
    if market == Market.SH:
        return f"{code}.XSHG"
    if market == Market.SZ:
        return f"{code}.XSHE"
    if market == Market.BJ:
        return f"{code}.BJSE"
    return symbol.strip().upper()


def to_ftshare_index_symbol(symbol: str) -> str:
    """Convert common index symbols to FTShare index format."""

    return to_ftshare_stock_symbol(symbol)


def to_cn_suffix(symbol: str) -> str:
    """Convert XSHG/XSHE/BJSE suffixes to SH/SZ/BJ suffixes."""

    text = symbol.strip().upper()
    return (
        text.replace(".XSHG", ".SH")
        .replace(".XSHE", ".SZ")
        .replace(".BJSE", ".BJ")
    )

