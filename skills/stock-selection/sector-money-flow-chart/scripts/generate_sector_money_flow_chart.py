"""Generate vertical A-share sector intraday money-flow style charts.

The script is deliberately strict about data quality:
- CSV mode can represent real minute sector net inflow when the CSV provides it.
- Eastmoney board mode is a proxy based on board intraday price/amount data.
- Demo mode is style-only simulated data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TRADE_TIMES = (
    [f"{h:02d}:{m:02d}" for h in [9] for m in range(30, 60)]
    + [f"10:{m:02d}" for m in range(0, 60)]
    + [f"11:{m:02d}" for m in range(0, 31)]
    + [f"13:{m:02d}" for m in range(0, 60)]
    + [f"14:{m:02d}" for m in range(0, 60)]
    + ["15:00"]
)


@dataclass
class Series:
    name: str
    values: list[float]
    color: str


@dataclass
class ChartResult:
    status: str
    data_level: str
    source: str
    note: str
    series: list[Series]
    times: list[str]


COLORS = [
    "#ff7676",
    "#77aaff",
    "#8ddc8d",
    "#7dd3fc",
    "#ffd166",
    "#ff9f80",
    "#ffb86c",
    "#f8c8dc",
    "#d084ff",
    "#b197fc",
    "#ffcc66",
    "#d6f5a3",
    "#54d4c8",
    "#68b7ff",
    "#6ee7b7",
    "#8dd0ff",
    "#ff87c1",
    "#a5b4fc",
    "#c084fc",
    "#86efac",
    "#fda4af",
]


DEMO_TARGETS = [
    ("半导体", 120.7),
    ("存储芯片", 116.6),
    ("军工", 5.4),
    ("车联网", 1.1),
    ("商业航天", -0.3),
    ("油气", -8.2),
    ("机器人", -12.3),
    ("白酒", -12.4),
    ("创新药", -16.8),
    ("证券", -19.4),
    ("铜矿", -19.5),
    ("CPO", -20.6),
    ("液冷", -25.3),
    ("光纤", -32.0),
    ("AI应用", -32.1),
    ("核聚变", -44.2),
    ("电网", -48.3),
    ("电池", -49.6),
    ("光伏", -53.0),
    ("稀土", -55.3),
    ("化工", -56.7),
    ("储能", -89.6),
    ("有色", -98.2),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sector intraday money-flow chart.")
    parser.add_argument("--date", required=True, help="Trade date, e.g. 2026-06-22.")
    parser.add_argument("--mode", choices=["csv", "eastmoney-board", "ftshare-aggregate", "demo"], default="demo")
    parser.add_argument("--input-csv", help="CSV with columns: time,sector,value_yi.")
    parser.add_argument("--sectors", default="", help="Comma-separated board names for eastmoney-board mode.")
    parser.add_argument("--board-type", choices=["concept", "industry"], default="concept")
    parser.add_argument("--period", default="5", choices=["1", "5", "15", "30", "60"])
    parser.add_argument("--top-n", type=int, default=23)
    parser.add_argument("--sample-size", type=int, default=80, help="Number of top-turnover stocks used by ftshare-aggregate.")
    parser.add_argument("--min-sector-count", type=int, default=2, help="Minimum sampled stocks for a sector in ftshare-aggregate.")
    parser.add_argument("--ftshare-run-py", default="", help="Path to ftshare-market-data run.py.")
    parser.add_argument("--fallback-demo", action="store_true", help="Use demo data if live board fetch fails.")
    parser.add_argument("--out-dir", default="reports/sector-money-flow")
    return parser.parse_args()


def demo_series() -> ChartResult:
    random.seed(17)
    times = sample_times(78)
    series: list[Series] = []
    for idx, (name, target) in enumerate(DEMO_TARGETS):
        series.append(Series(name=name, values=demo_curve(target, len(times), idx), color=COLORS[idx % len(COLORS)]))
    return ChartResult(
        status="completed",
        data_level="demo",
        source="local:simulated",
        note="样式验证数据，不代表真实板块主力净流入。",
        series=series,
        times=times,
    )


def demo_curve(target: float, length: int, idx: int) -> list[float]:
    vals: list[float] = []
    for i in range(length):
        t = i / (length - 1)
        if idx == 0:
            base = target * (0.03 * math.sin(t * 18) + 0.18 * t + 0.82 / (1 + math.exp(-(t - 0.62) * 24)))
        elif idx == 1:
            base = target * (0.08 * math.sin(t * 16) + 0.14 * t + 0.82 / (1 + math.exp(-(t - 0.58) * 20)))
        elif target >= 0:
            base = target * (math.sin(t * 5 + idx) * 0.12 + t**1.2)
        else:
            base = target * (t**1.05) + abs(target) * 0.12 * math.sin(t * 9 + idx * 0.7)
            if -30 < target < 0:
                base += abs(target) * 0.35 * math.exp(-((t - 0.22 - idx * 0.01) / 0.16) ** 2)
        vals.append(base + (random.random() - 0.5) * max(3, abs(target) * 0.035))
    vals[0] = 0
    vals[-1] = target
    return vals


def sample_times(length: int) -> list[str]:
    if length >= len(TRADE_TIMES):
        return TRADE_TIMES[:]
    indexes = [round(i * (len(TRADE_TIMES) - 1) / (length - 1)) for i in range(length)]
    return [TRADE_TIMES[i] for i in indexes]


def load_csv(input_csv: Path, top_n: int) -> ChartResult:
    grouped: dict[str, dict[str, float]] = {}
    times: list[str] = []
    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"time", "sector", "value_yi"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")
        for row in reader:
            time = str(row["time"]).strip()
            sector = str(row["sector"]).strip()
            if not time or not sector:
                continue
            if time not in times:
                times.append(time)
            grouped.setdefault(sector, {})[time] = float(row["value_yi"])
    ranked = sorted(grouped.items(), key=lambda item: abs(item[1].get(times[-1], 0.0)), reverse=True)[:top_n]
    series = []
    for idx, (sector, values_by_time) in enumerate(ranked):
        values = forward_fill([values_by_time.get(t) for t in times])
        series.append(Series(sector, values, COLORS[idx % len(COLORS)]))
    return ChartResult(
        status="completed",
        data_level="real",
        source=str(input_csv),
        note="CSV输入被视为真实分钟板块主力净流入；请确认 value_yi 口径为累计净流入亿元。",
        series=series,
        times=times,
    )


def forward_fill(values: Iterable[float | None]) -> list[float]:
    out: list[float] = []
    last = 0.0
    for value in values:
        if value is not None:
            last = float(value)
        out.append(last)
    return out


def load_eastmoney_board(sectors: list[str], board_type: str, period: str, top_n: int, fallback_demo: bool) -> ChartResult:
    try:
        import akshare as ak  # type: ignore
    except Exception as exc:  # pragma: no cover
        if fallback_demo:
            result = demo_series()
            result.status = "degraded"
            result.note = f"AkShare不可用，已回退demo: {exc}"
            return result
        raise

    if not sectors:
        sectors = ["半导体", "存储芯片", "证券", "有色金属", "机器人", "CPO", "光模块", "AI应用"]

    fetch = ak.stock_board_concept_hist_min_em if board_type == "concept" else ak.stock_board_industry_hist_min_em
    raw: list[tuple[str, list[str], list[float]]] = []
    errors: list[str] = []
    for sector in sectors:
        try:
            df = fetch(symbol=sector, period=period)
            times, values = board_df_to_proxy(df)
            if times and values:
                raw.append((sector, times, values))
        except Exception as exc:
            errors.append(f"{sector}: {exc}")

    if not raw:
        if fallback_demo:
            result = demo_series()
            result.status = "degraded"
            result.note = "Eastmoney板块分钟接口失败，已回退demo: " + " | ".join(errors[:3])
            return result
        raise RuntimeError("Eastmoney board minute data unavailable: " + " | ".join(errors[:5]))

    base_times = raw[0][1]
    ranked = sorted(raw, key=lambda item: abs(item[2][-1]), reverse=True)[:top_n]
    series = [Series(name, align_values(times, values, base_times), COLORS[idx % len(COLORS)]) for idx, (name, times, values) in enumerate(ranked)]
    note = "Eastmoney板块分钟行情代理：value_yi 为相对涨跌/成交额强度缩放值，不等于真实主力净流入。"
    if errors:
        note += " 部分板块失败: " + " | ".join(errors[:5])
    return ChartResult("degraded", "proxy", f"eastmoney:{board_type}:hist_min:{period}", note, series, base_times)


def load_ftshare_aggregate(args: argparse.Namespace) -> ChartResult:
    run_py = Path(args.ftshare_run_py) if args.ftshare_run_py else Path.home() / ".codex" / "skills" / "ftshare-market-data" / "run.py"
    if not run_py.exists():
        if args.fallback_demo:
            result = demo_series()
            result.status = "degraded"
            result.note = f"FTShare run.py not found, fallback demo: {run_py}"
            return result
        raise FileNotFoundError(f"FTShare run.py not found: {run_py}")

    quotes = call_ftshare(
        run_py,
        [
            "stock-quotes-list",
            "--order_by",
            "turnover desc",
            "--page_no",
            "1",
            "--page_size",
            str(args.sample_size),
        ],
    )
    stocks = quotes.get("stocks") or []
    grouped: dict[str, list[dict]] = {}
    for stock in stocks:
        sector = ((stock.get("industry_sector") or {}).get("name") or "").strip()
        symkey = (stock.get("symkey") or "").strip()
        if sector and symkey:
            grouped.setdefault(sector, []).append(stock)

    sector_values: dict[str, dict[str, float]] = {}
    sector_counts: dict[str, int] = {}
    errors: list[str] = []
    for sector, items in grouped.items():
        if len(items) < args.min_sector_count:
            continue
        for item in items:
            symkey = item["symkey"]
            try:
                prices_reply = call_ftshare(run_py, ["stock-prices", "--stock", symkey, "--since", "TODAY"])
                minute_values = signed_amount_curve(prices_reply)
                if not minute_values:
                    continue
                bucket = sector_values.setdefault(sector, {})
                for time, value_yi in minute_values.items():
                    bucket[time] = bucket.get(time, 0.0) + value_yi
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            except Exception as exc:
                errors.append(f"{symkey}: {exc}")

    if not sector_values:
        if args.fallback_demo:
            result = demo_series()
            result.status = "degraded"
            result.note = "FTShare aggregate failed, fallback demo: " + " | ".join(errors[:3])
            return result
        raise RuntimeError("FTShare aggregate produced no usable sector series: " + " | ".join(errors[:5]))

    all_times = sorted({time for values in sector_values.values() for time in values})
    ranked = sorted(
        sector_values.items(),
        key=lambda item: abs(forward_fill([item[1].get(t) for t in all_times])[-1]),
        reverse=True,
    )[: args.top_n]
    series: list[Series] = []
    for idx, (sector, values_by_time) in enumerate(ranked):
        values = forward_fill([values_by_time.get(t) for t in all_times])
        label = f"{sector}"
        series.append(Series(label, values, COLORS[idx % len(COLORS)]))

    note = (
        "FTShare aggregate proxy: top-turnover sampled stocks are grouped by industry_sector; "
        "minute turnover is signed by price direction and accumulated in 100m CNY units. "
        "This is not real main-fund net inflow."
    )
    if errors:
        note += " Partial failures: " + " | ".join(errors[:5])
    return ChartResult(
        status="degraded",
        data_level="proxy",
        source=f"ftshare:stock-quotes-list+stock-prices:sample={args.sample_size}",
        note=note,
        series=series,
        times=all_times,
    )


def call_ftshare(run_py: Path, params: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(run_py), *params],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def signed_amount_curve(prices_reply: dict) -> dict[str, float]:
    prices = prices_reply.get("prices") or []
    prev_close = prices_reply.get("prev_close")
    last_price = float(prev_close) if prev_close else None
    cumulative = 0.0
    out: dict[str, float] = {}
    for rec in prices:
        price = rec.get("p")
        amount = float(rec.get("t") or 0.0)
        time = normalize_time(rec.get("tm"))
        if price is None or not time:
            continue
        price = float(price)
        if last_price is None:
            sign = 0.0
        elif price > last_price:
            sign = 1.0
        elif price < last_price:
            sign = -1.0
        else:
            sign = 0.0
        cumulative += sign * amount / 100_000_000
        out[time] = cumulative
        last_price = price
    return out


def board_df_to_proxy(df) -> tuple[list[str], list[float]]:
    columns = {str(c): c for c in df.columns}
    time_col = first_existing(columns, ["时间", "日期", "datetime", "time"])
    close_col = first_existing(columns, ["收盘", "最新价", "close"])
    amount_col = first_existing(columns, ["成交额", "amount"])
    if time_col is None or close_col is None:
        return [], []
    times = [normalize_time(v) for v in df[time_col].tolist()]
    closes = [float(v) for v in df[close_col].tolist()]
    first = closes[0] if closes else 0.0
    if not first:
        return [], []
    pct = [(v / first - 1.0) * 100.0 for v in closes]
    if amount_col is not None:
        amounts = [float(v) for v in df[amount_col].tolist()]
        scale = max(max(amounts) / 100_000_000, 1.0) if amounts else 1.0
    else:
        scale = 10.0
    values = [v * min(scale, 35.0) for v in pct]
    return times, values


def first_existing(columns: dict[str, object], names: list[str]):
    for name in names:
        if name in columns:
            return columns[name]
    return None


def normalize_time(value: object) -> str:
    text = str(value)
    if "T" in text:
        text = text.split("T")[-1]
    if " " in text:
        text = text.split()[-1]
    return text[:5]


def align_values(times: list[str], values: list[float], base_times: list[str]) -> list[float]:
    mapping = dict(zip(times, values))
    return forward_fill([mapping.get(t) for t in base_times])


def write_csv(path: Path, result: ChartResult) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "sector", "value_yi", "data_level", "source"])
        for series in result.series:
            for time, value in zip(result.times, series.values):
                writer.writerow([time, series.name, round(value, 4), result.data_level, result.source])


def write_quality(
    path: Path,
    args: argparse.Namespace,
    result: ChartResult,
    svg_path: Path,
    csv_path: Path,
    html_path: Path,
    index_path: Path,
) -> None:
    lines = [
        f"# {args.date} Sector Money Flow Chart Quality",
        "",
        f"- status: `{result.status}`",
        f"- data_level: `{result.data_level}`",
        f"- source: `{result.source}`",
        f"- svg: `{svg_path}`",
        f"- csv: `{csv_path}`",
        f"- html: `{html_path}`",
        f"- full_screen_player: `{index_path}`",
        f"- note: {result.note}",
        "",
        "## Interpretation",
    ]
    if result.data_level == "real":
        lines.append("- 可用于观察板块主力资金净流入的持续性、尾盘抢筹、冲高回落和分歧。")
    elif result.data_level == "proxy":
        lines.append("- 只能作为板块分时强弱代理，不能当作真实主力净流入金额。")
    else:
        lines.append("- 仅用于图形样式验证，不用于交易判断。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_html(result: ChartResult, title_date: str, out: Path) -> None:
    payload = {
        "date": title_date,
        "times": result.times,
        "dataLevel": result.data_level,
        "source": result.source,
        "note": result.note,
        "series": [
            {"name": series.name, "color": series.color, "values": [round(v, 4) for v in series.values]}
            for series in result.series
        ],
    }
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title_date} 板块资金流动画</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      background: #050914;
      color: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background:
        radial-gradient(circle at 52% 34%, rgba(32, 63, 108, 0.32), transparent 42%),
        linear-gradient(180deg, #050914 0%, #0a1020 58%, #050914 100%);
    }}
    .shell {{
      width: min(100vw, 540px);
      padding: 14px;
    }}
    .stage {{
      position: relative;
      border: 1px solid #172033;
      border-radius: 10px;
      overflow: hidden;
      background: #07101f;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
    }}
    canvas {{
      display: block;
      width: 100%;
      height: auto;
      aspect-ratio: 5 / 9;
    }}
    .controls {{
      position: absolute;
      left: 0;
      right: 0;
      top: 10px;
      display: flex;
      justify-content: center;
      gap: 8px;
      pointer-events: none;
    }}
    button {{
      pointer-events: auto;
      height: 28px;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 0 12px;
      color: #dbeafe;
      background: rgba(15, 23, 42, 0.78);
      font-size: 12px;
      cursor: pointer;
    }}
    button.active {{ background: #2563eb; color: white; border-color: #60a5fa; }}
    .meta {{
      margin-top: 10px;
      color: #94a3b8;
      font-size: 12px;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="stage">
      <canvas id="chart" width="500" height="900"></canvas>
      <div class="controls">
        <button id="replay">重新播放</button>
        <button class="speed" data-speed="0.5">0.5x</button>
        <button class="speed active" data-speed="1">1.0x</button>
        <button class="speed" data-speed="2">2.0x</button>
      </div>
    </section>
    <div class="meta" id="meta"></div>
  </main>
  <script id="chart-data" type="application/json">{data_json}</script>
  <script>
    const data = JSON.parse(document.getElementById("chart-data").textContent);
    const canvas = document.getElementById("chart");
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;
    const pad = {{ left: 48, right: 132, top: 82, bottom: 56 }};
    const plotW = W - pad.left - pad.right;
    const plotH = H - pad.top - pad.bottom;
    const allValues = data.series.flatMap(s => s.values);
    const maxAbs = Math.max(120, ...allValues.map(v => Math.abs(v)));
    const yMax = Math.max(140, Math.ceil(maxAbs / 20) * 20);
    const yMin = Math.min(-120, -Math.ceil(maxAbs / 20) * 20);
    let frame = 1;
    let playing = true;
    let speed = 1;
    let lastTs = 0;

    document.getElementById("meta").textContent =
      `${{data.dataLevel}} | ${{data.source}} | ${{data.note}}`;

    document.getElementById("replay").addEventListener("click", () => {{
      frame = 1;
      playing = true;
    }});
    document.querySelectorAll(".speed").forEach(btn => {{
      btn.addEventListener("click", () => {{
        speed = Number(btn.dataset.speed);
        document.querySelectorAll(".speed").forEach(item => item.classList.remove("active"));
        btn.classList.add("active");
      }});
    }});
    canvas.addEventListener("click", () => {{
      playing = !playing;
    }});

    function yOf(value) {{
      return pad.top + (yMax - value) / (yMax - yMin) * plotH;
    }}

    function xOf(index) {{
      const n = Math.max(data.times.length, 2);
      return pad.left + index * plotW / (n - 1);
    }}

    function roundRect(x, y, w, h, r, fill, stroke) {{
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
      if (fill) {{
        ctx.fillStyle = fill;
        ctx.fill();
      }}
      if (stroke) {{
        ctx.strokeStyle = stroke;
        ctx.stroke();
      }}
    }}

    function drawBackground() {{
      const bg = ctx.createRadialGradient(W * 0.5, H * 0.42, 20, W * 0.5, H * 0.42, H * 0.82);
      bg.addColorStop(0, "#101b2f");
      bg.addColorStop(0.65, "#0b1220");
      bg.addColorStop(1, "#060913");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);
      ctx.strokeStyle = "#111827";
      ctx.lineWidth = 2;
      roundRect(6, 8, 488, 884, 8, null, "#111827");

      ctx.font = "800 28px Arial";
      ctx.fillStyle = "#ff9f7a";
      ctx.fillText(data.date.slice(5), 50, 67);
      ctx.font = "800 28px Microsoft YaHei, Arial";
      ctx.fillStyle = "#ffe082";
      ctx.fillText("主力资金净流入", 137, 67);
      ctx.font = "700 24px Arial";
      ctx.fillStyle = "#7dd3a7";
      ctx.fillText(`(${{data.times[Math.min(frame - 1, data.times.length - 1)] || "15:00"}})`, 368, 67);
    }}

    function drawAxes() {{
      const ticks = [yMax, 100, 50, 0, -50, -100, yMin];
      const seen = new Set();
      ctx.font = "13px Arial";
      ticks.forEach(value => {{
        if (seen.has(value) || value < yMin || value > yMax) return;
        seen.add(value);
        const y = yOf(value);
        ctx.strokeStyle = "rgba(38, 50, 65, 0.75)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(W - pad.right, y);
        ctx.stroke();
        ctx.fillStyle = "#cbd5e1";
        ctx.fillText(`${{value}}亿`, 8, y + 5);
      }});
      [["09:30", 0], ["10:30", 0.25], ["11:30", 0.50], ["14:00", 0.78], ["15:00", 1]].forEach(([label, ratio]) => {{
        ctx.fillStyle = "#cbd5e1";
        ctx.font = "12px Arial";
        ctx.fillText(label, pad.left + ratio * plotW - 15, H - 27);
      }});
    }}

    function drawSeries() {{
      const visible = Math.max(1, Math.min(frame, data.times.length));
      const endpoints = [];
      data.series.forEach(series => {{
        ctx.beginPath();
        for (let i = 0; i < visible; i += 1) {{
          const x = xOf(i);
          const y = yOf(series.values[i]);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }}
        ctx.strokeStyle = series.color;
        ctx.lineWidth = 2.3;
        ctx.globalAlpha = 0.94;
        ctx.shadowColor = series.color;
        ctx.shadowBlur = 3;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
        const lastIndex = visible - 1;
        endpoints.push({{
          name: series.name,
          color: series.color,
          value: series.values[lastIndex],
          x: xOf(lastIndex),
          y: yOf(series.values[lastIndex])
        }});
      }});
      drawLabels(endpoints);
    }}

    function drawLabels(endpoints) {{
      const sorted = endpoints.sort((a, b) => a.y - b.y);
      let lastY = pad.top - 99;
      const labelX = W - pad.right + 8;
      sorted.forEach(point => {{
        let y = Math.max(pad.top + 12, Math.min(H - pad.bottom - 18, point.y));
        if (y < lastY + 25) y = lastY + 25;
        y = Math.min(y, H - pad.bottom - 16);
        lastY = y;
        ctx.fillStyle = point.color;
        ctx.beginPath();
        ctx.arc(point.x, point.y, 4.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#e5e7eb";
        ctx.lineWidth = 0.8;
        ctx.stroke();
        ctx.strokeStyle = point.color;
        ctx.globalAlpha = 0.65;
        ctx.beginPath();
        ctx.moveTo(point.x + 4, point.y);
        ctx.lineTo(labelX - 3, y);
        ctx.stroke();
        ctx.globalAlpha = 1;
        roundRect(labelX, y - 12, 106, 22, 4, "rgba(11,18,32,0.92)", point.color);
        ctx.fillStyle = point.color;
        ctx.font = "12.5px Microsoft YaHei, Arial";
        ctx.fillText(`${{point.name}} ${{point.value.toFixed(1)}}`, labelX + 6, y + 4, 96);
      }});
    }}

    function drawFooter() {{
      const levelText = {{ real: "真实分钟资金流", proxy: "代理数据", demo: "演示数据" }}[data.dataLevel] || data.dataLevel;
      ctx.fillStyle = "rgba(229, 231, 235, 0.65)";
      ctx.font = "11px Microsoft YaHei, Arial";
      ctx.fillText(`${{levelText}}：${{data.note.slice(0, 30)}}`, 250, 882, 230);
    }}

    function render(ts) {{
      if (!lastTs) lastTs = ts;
      const elapsed = ts - lastTs;
      if (playing && elapsed > 42 / speed) {{
        frame += 1;
        if (frame > data.times.length) {{
          frame = data.times.length;
          playing = false;
        }}
        lastTs = ts;
      }}
      ctx.clearRect(0, 0, W, H);
      drawBackground();
      drawAxes();
      drawSeries();
      drawFooter();
      requestAnimationFrame(render);
    }}

    requestAnimationFrame(render);
  </script>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")


def load_csv_payload(csv_path: Path) -> dict:
    grouped: dict[str, dict[str, float]] = {}
    times: list[str] = []
    data_level = "unknown"
    source = str(csv_path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            time = str(row.get("time", "")).strip()
            sector = str(row.get("sector", "")).strip()
            if not time or not sector:
                continue
            if time not in times:
                times.append(time)
            grouped.setdefault(sector, {})[time] = float(row.get("value_yi") or 0.0)
            data_level = str(row.get("data_level") or data_level)
            source = str(row.get("source") or source)
    ranked = sorted(grouped.items(), key=lambda item: abs(item[1].get(times[-1], 0.0)) if times else 0.0, reverse=True)
    series = [
        {
            "name": sector,
            "color": COLORS[idx % len(COLORS)],
            "values": [round(v, 4) for v in forward_fill([values_by_time.get(t) for t in times])],
        }
        for idx, (sector, values_by_time) in enumerate(ranked)
    ]
    date = csv_path.name.replace("-sector-money-flow.csv", "")
    return {
        "date": date,
        "times": times,
        "dataLevel": data_level,
        "source": source,
        "note": "CSV replay dataset loaded from generated sector-money-flow output.",
        "series": series,
    }


def render_index_html(out_dir: Path, out: Path) -> None:
    datasets = []
    for csv_path in sorted(out_dir.glob("*-sector-money-flow.csv")):
        try:
            payload = load_csv_payload(csv_path)
            if payload["times"] and payload["series"]:
                datasets.append(payload)
        except Exception:
            continue
    if not datasets:
        return
    data_json = json.dumps({"datasets": datasets}, ensure_ascii=False).replace("</", "<\\/")
    html_template = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>板块资金流全屏播放器</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      background: #050914;
      color: #e5e7eb;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; }
    body {
      background:
        radial-gradient(circle at 50% 36%, rgba(40, 77, 129, 0.32), transparent 44%),
        linear-gradient(180deg, #050914 0%, #0b1220 62%, #050914 100%);
    }
    canvas {
      display: block;
      width: 100vw;
      height: 100vh;
    }
    .toolbar {
      position: fixed;
      right: 18px;
      top: 14px;
      z-index: 2;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border: 1px solid rgba(96, 165, 250, 0.28);
      border-radius: 999px;
      background: rgba(8, 13, 26, 0.72);
      backdrop-filter: blur(10px);
      box-shadow: 0 16px 60px rgba(0, 0, 0, 0.34);
    }
    @media (max-width: 760px) {
      .toolbar {
        left: 10px;
        right: 10px;
        justify-content: center;
        flex-wrap: wrap;
        border-radius: 18px;
      }
      select, button {
        height: 28px;
        font-size: 12px;
        padding: 0 9px;
      }
      select { min-width: 120px; }
    }
    select, button {
      height: 30px;
      border: 1px solid #334155;
      border-radius: 15px;
      padding: 0 12px;
      color: #dbeafe;
      background: rgba(15, 23, 42, 0.9);
      font-size: 13px;
      outline: none;
    }
    select { min-width: 138px; }
    button { cursor: pointer; }
    button.active { background: #2563eb; color: #fff; border-color: #60a5fa; }
    .meta {
      display: none;
    }
  </style>
</head>
<body>
  <canvas id="chart"></canvas>
  <div class="toolbar">
    <select id="dateSelect" title="选择交易日"></select>
    <button id="replay">重新播放</button>
    <button class="speed" data-speed="0.5">0.5x</button>
    <button class="speed active" data-speed="1">1.0x</button>
    <button class="speed" data-speed="2">2.0x</button>
    <button id="toggle">暂停</button>
  </div>
  <div class="meta" id="meta"></div>
  <script id="chart-data" type="application/json">__DATA__</script>
  <script>
    const store = JSON.parse(document.getElementById("chart-data").textContent);
    const canvas = document.getElementById("chart");
    const ctx = canvas.getContext("2d");
    const select = document.getElementById("dateSelect");
    const meta = document.getElementById("meta");
    let data = store.datasets[store.datasets.length - 1];
    let frame = 1;
    let playing = true;
    let speed = 1;
    let lastTs = 0;
    let dims = {};

    store.datasets.forEach((item, index) => {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = item.date;
      select.appendChild(option);
    });
    select.value = String(store.datasets.length - 1);

    function resetForDataset(nextData) {
      data = nextData;
      frame = 1;
      playing = true;
      lastTs = 0;
      updateMeta();
    }

    function updateMeta() {
      meta.textContent = `${data.date} | ${data.dataLevel} | ${data.source} | ${data.note}`;
      document.getElementById("toggle").textContent = playing ? "暂停" : "播放";
    }

    select.addEventListener("change", () => resetForDataset(store.datasets[Number(select.value)]));
    document.getElementById("replay").addEventListener("click", () => resetForDataset(data));
    document.getElementById("toggle").addEventListener("click", () => {
      playing = !playing;
      updateMeta();
    });
    document.querySelectorAll(".speed").forEach(btn => {
      btn.addEventListener("click", () => {
        speed = Number(btn.dataset.speed);
        document.querySelectorAll(".speed").forEach(item => item.classList.remove("active"));
        btn.classList.add("active");
      });
    });
    canvas.addEventListener("click", () => {
      playing = !playing;
      updateMeta();
    });

    function resize() {
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dims = {
        w: window.innerWidth,
        h: window.innerHeight,
        left: Math.max(48, window.innerWidth * 0.07),
        right: Math.max(150, window.innerWidth * 0.24),
        top: Math.max(138, window.innerHeight * 0.16),
        bottom: Math.max(58, window.innerHeight * 0.08)
      };
      dims.plotW = dims.w - dims.left - dims.right;
      dims.plotH = dims.h - dims.top - dims.bottom;
    }
    window.addEventListener("resize", resize);
    resize();

    function scaleInfo() {
      const allValues = data.series.flatMap(s => s.values);
      const maxAbs = Math.max(120, ...allValues.map(v => Math.abs(v)));
      return {
        yMax: Math.max(140, Math.ceil(maxAbs / 20) * 20),
        yMin: Math.min(-120, -Math.ceil(maxAbs / 20) * 20)
      };
    }

    function yOf(value, scale) {
      return dims.top + (scale.yMax - value) / (scale.yMax - scale.yMin) * dims.plotH;
    }

    function xOf(index) {
      const n = Math.max(data.times.length, 2);
      return dims.left + index * dims.plotW / (n - 1);
    }

    function roundRect(x, y, w, h, r, fill, stroke) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
      if (fill) {
        ctx.fillStyle = fill;
        ctx.fill();
      }
      if (stroke) {
        ctx.strokeStyle = stroke;
        ctx.stroke();
      }
    }

    function drawBackground() {
      const bg = ctx.createRadialGradient(dims.w * 0.5, dims.h * 0.4, 20, dims.w * 0.5, dims.h * 0.4, dims.h * 0.82);
      bg.addColorStop(0, "#101b2f");
      bg.addColorStop(0.68, "#0b1220");
      bg.addColorStop(1, "#060913");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, dims.w, dims.h);

      const time = data.times[Math.min(frame - 1, data.times.length - 1)] || "15:00";
      const titleParts = [data.date.slice(5), "主力资金净流入", `(${time})`];
      const titleColors = ["#ff9f7a", "#ffe082", "#7dd3a7"];
      const titleFonts = ["Arial", "Microsoft YaHei, Arial", "Arial"];
      const maxTitleWidth = Math.max(320, dims.w - dims.left - dims.right - 20);
      let titleSize = Math.min(42, Math.max(24, dims.w * 0.026));
      let subTitleSize = Math.min(24, Math.max(17, dims.w * 0.018));
      let measured = Infinity;
      while (titleSize > 22) {
        ctx.font = `800 ${titleSize}px ${titleFonts[0]}`;
        const dateWidth = ctx.measureText(titleParts[0]).width;
        ctx.font = `800 ${titleSize}px ${titleFonts[1]}`;
        const titleWidth = ctx.measureText(titleParts[1]).width;
        ctx.font = `700 ${subTitleSize}px ${titleFonts[2]}`;
        const timeWidth = ctx.measureText(titleParts[2]).width;
        measured = dateWidth + titleWidth + timeWidth + titleSize * 0.72;
        if (measured <= maxTitleWidth) break;
        titleSize -= 2;
        subTitleSize = Math.max(15, subTitleSize - 1);
      }
      let titleX = dims.left;
      ctx.font = `800 ${titleSize}px Arial`;
      ctx.fillStyle = titleColors[0];
      ctx.fillText(titleParts[0], titleX, dims.top - 38);
      titleX += ctx.measureText(titleParts[0]).width + titleSize * 0.18;
      ctx.font = `800 ${titleSize}px Microsoft YaHei, Arial`;
      ctx.fillStyle = titleColors[1];
      ctx.fillText(titleParts[1], titleX, dims.top - 38);
      titleX += ctx.measureText(titleParts[1]).width + titleSize * 0.18;
      ctx.font = `700 ${subTitleSize}px Arial`;
      ctx.fillStyle = titleColors[2];
      ctx.fillText(titleParts[2], titleX, dims.top - 38);
    }

    function drawAxes(scale) {
      const ticks = [scale.yMax, 100, 50, 0, -50, -100, scale.yMin];
      const seen = new Set();
      ctx.font = "13px Arial";
      ticks.forEach(value => {
        if (seen.has(value) || value < scale.yMin || value > scale.yMax) return;
        seen.add(value);
        const y = yOf(value, scale);
        ctx.strokeStyle = "rgba(38, 50, 65, 0.78)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(dims.left, y);
        ctx.lineTo(dims.w - dims.right, y);
        ctx.stroke();
        ctx.fillStyle = "#cbd5e1";
        ctx.fillText(`${value}亿`, 10, y + 5);
      });
      [["09:30", 0], ["10:30", 0.25], ["11:30", 0.50], ["14:00", 0.78], ["15:00", 1]].forEach(([label, ratio]) => {
        ctx.fillStyle = "#cbd5e1";
        ctx.font = "12px Arial";
        ctx.fillText(label, dims.left + ratio * dims.plotW - 15, dims.h - 28);
      });
    }

    function drawSeries(scale) {
      const visible = Math.max(1, Math.min(frame, data.times.length));
      const endpoints = [];
      data.series.forEach(series => {
        ctx.beginPath();
        for (let i = 0; i < visible; i += 1) {
          const x = xOf(i);
          const y = yOf(series.values[i], scale);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = series.color;
        ctx.lineWidth = 2.5;
        ctx.globalAlpha = 0.94;
        ctx.shadowColor = series.color;
        ctx.shadowBlur = 3;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
        const lastIndex = visible - 1;
        endpoints.push({
          name: series.name,
          color: series.color,
          value: series.values[lastIndex],
          x: xOf(lastIndex),
          y: yOf(series.values[lastIndex], scale)
        });
      });
      drawLabels(endpoints);
    }

    function drawLabels(endpoints) {
      const sorted = endpoints.sort((a, b) => a.y - b.y);
      let lastY = dims.top - 99;
      const labelX = dims.w - dims.right + 8;
      sorted.forEach(point => {
        let y = Math.max(dims.top + 12, Math.min(dims.h - dims.bottom - 18, point.y));
        if (y < lastY + 25) y = lastY + 25;
        y = Math.min(y, dims.h - dims.bottom - 16);
        lastY = y;
        ctx.fillStyle = point.color;
        ctx.beginPath();
        ctx.arc(point.x, point.y, 4.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#e5e7eb";
        ctx.lineWidth = 0.8;
        ctx.stroke();
        ctx.strokeStyle = point.color;
        ctx.globalAlpha = 0.65;
        ctx.beginPath();
        ctx.moveTo(point.x + 4, point.y);
        ctx.lineTo(labelX - 3, y);
        ctx.stroke();
        ctx.globalAlpha = 1;
        roundRect(labelX, y - 12, 132, 22, 4, "rgba(11,18,32,0.92)", point.color);
        ctx.fillStyle = point.color;
        ctx.font = "12.5px Microsoft YaHei, Arial";
        ctx.fillText(`${point.name} ${point.value.toFixed(1)}`, labelX + 6, y + 4, 120);
      });
    }

    function render(ts) {
      if (!lastTs) lastTs = ts;
      const elapsed = ts - lastTs;
      if (playing && elapsed > 42 / speed) {
        frame += 1;
        if (frame > data.times.length) {
          frame = data.times.length;
          playing = false;
          updateMeta();
        }
        lastTs = ts;
      }
      const scale = scaleInfo();
      ctx.clearRect(0, 0, dims.w, dims.h);
      drawBackground();
      drawAxes(scale);
      drawSeries(scale);
      requestAnimationFrame(render);
    }

    updateMeta();
    requestAnimationFrame(render);
  </script>
</body>
</html>
"""
    out.write_text(html_template.replace("__DATA__", data_json), encoding="utf-8")


def render_svg(result: ChartResult, title_date: str, as_of: str, out: Path) -> None:
    width, height = 500, 900
    left, right, top, bottom = 48, 132, 82, 56
    plot_w, plot_h = width - left - right, height - top - bottom
    max_abs = max([abs(v) for s in result.series for v in s.values] + [120.0])
    y_max = max(140.0, math.ceil(max_abs / 20) * 20)
    y_min = min(-120.0, -math.ceil(max_abs / 20) * 20)

    def y_of(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_h

    n = max(len(result.times), 2)
    xs = [left + i * plot_w / (n - 1) for i in range(n)]
    paths = []
    for series in result.series:
        pts = [(x, y_of(v)) for x, v in zip(xs, series.values)]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        paths.append((series, d, pts[-1]))

    lines: list[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    lines.append('<defs><radialGradient id="bg" cx="50%" cy="42%" r="80%"><stop offset="0" stop-color="#101b2f"/><stop offset="0.65" stop-color="#0b1220"/><stop offset="1" stop-color="#060913"/></radialGradient><filter id="glow"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    lines.append(f'<rect width="{width}" height="{height}" fill="url(#bg)"/>')
    lines.append('<rect x="6" y="8" width="488" height="884" rx="8" fill="none" stroke="#111827" stroke-width="2"/>')
    lines.append('<rect x="127" y="18" width="78" height="26" rx="13" fill="#1f2937" opacity="0.9"/><text x="145" y="36" fill="#cbd5e1" font-size="13" font-family="Microsoft YaHei">重新播放</text>')
    lines.append('<rect x="218" y="18" width="42" height="26" rx="13" fill="#111827" stroke="#334155"/><text x="226" y="36" fill="#cbd5e1" font-size="13">0.5x</text>')
    lines.append('<rect x="267" y="18" width="48" height="26" rx="13" fill="#2563eb"/><text x="278" y="36" fill="white" font-size="13">1.0x</text>')
    lines.append('<rect x="321" y="18" width="42" height="26" rx="13" fill="#111827" stroke="#334155"/><text x="329" y="36" fill="#cbd5e1" font-size="13">2.0x</text>')
    lines.append(f'<text x="50" y="67" fill="#ff9f7a" font-size="28" font-weight="800" font-family="Arial">{title_date[5:]}</text><text x="137" y="67" fill="#ffe082" font-size="28" font-weight="800" font-family="Microsoft YaHei">主力资金净流入</text><text x="368" y="67" fill="#7dd3a7" font-size="24" font-weight="700" font-family="Arial">({as_of})</text>')
    tick_values = [y_max, 100, 50, 0, -50, -100, y_min]
    seen = set()
    for value in tick_values:
        if value in seen or value < y_min or value > y_max:
            continue
        seen.add(value)
        y = y_of(value)
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#263241" stroke-width="1" opacity="0.75"/>')
        lines.append(f'<text x="8" y="{y+5:.1f}" fill="#cbd5e1" font-size="13" font-family="Arial">{value:g}亿</text>')
    for label, ratio in [("09:30", 0), ("10:30", 0.25), ("11:30", 0.50), ("14:00", 0.78), ("15:00", 1.0)]:
        x = left + ratio * plot_w
        lines.append(f'<text x="{x-15:.1f}" y="{height-27}" fill="#cbd5e1" font-size="12" font-family="Arial">{label}</text>')
    for series, d, _ in paths:
        lines.append(f'<path d="{d}" fill="none" stroke="{series.color}" stroke-width="2.3" opacity="0.94" filter="url(#glow)"/>')
    label_x = width - right + 8
    last_y = top - 99
    for series, _, end in sorted(paths, key=lambda item: item[2][1]):
        ex, ey = end
        y = max(top + 12, min(height - bottom - 18, ey))
        if y < last_y + 25:
            y = last_y + 25
        y = min(y, height - bottom - 16)
        last_y = y
        latest = series.values[-1]
        lines.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.2" fill="{series.color}" stroke="#e5e7eb" stroke-width="0.8"/>')
        lines.append(f'<line x1="{ex+4:.1f}" y1="{ey:.1f}" x2="{label_x-3}" y2="{y:.1f}" stroke="{series.color}" stroke-width="1" opacity="0.65"/>')
        lines.append(f'<rect x="{label_x}" y="{y-12:.1f}" width="106" height="22" rx="4" fill="#0b1220" stroke="{series.color}" stroke-width="1" opacity="0.92"/>')
        lines.append(f'<text x="{label_x+6}" y="{y+4:.1f}" fill="{series.color}" font-size="12.5" font-family="Microsoft YaHei, Arial">{series.name} {latest:.1f}</text>')
    level_note = {"real": "真实分钟资金流", "proxy": "代理数据", "demo": "演示数据"}[result.data_level]
    lines.append(f'<text x="250" y="882" fill="#e5e7eb" opacity="0.65" font-size="11" font-family="Microsoft YaHei">{level_note}：{result.note[:28]}</text>')
    lines.append("</svg>")
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "csv":
        if not args.input_csv:
            raise SystemExit("--input-csv is required for csv mode")
        result = load_csv(Path(args.input_csv), args.top_n)
    elif args.mode == "eastmoney-board":
        sectors = [s.strip() for s in args.sectors.split(",") if s.strip()]
        result = load_eastmoney_board(sectors, args.board_type, args.period, args.top_n, args.fallback_demo)
    elif args.mode == "ftshare-aggregate":
        result = load_ftshare_aggregate(args)
    else:
        result = demo_series()

    stem = f"{args.date}-sector-money-flow"
    svg_path = out_dir / f"{stem}.svg"
    html_path = out_dir / f"{stem}.html"
    csv_path = out_dir / f"{stem}.csv"
    quality_path = out_dir / f"{stem}-quality.md"
    as_of = result.times[-1] if result.times else "15:00"
    render_svg(result, args.date, as_of, svg_path)
    render_html(result, args.date, html_path)
    write_csv(csv_path, result)
    index_path = out_dir / "index.html"
    render_index_html(out_dir, index_path)
    write_quality(quality_path, args, result, svg_path, csv_path, html_path, index_path)
    print(svg_path.resolve())
    print(html_path.resolve())
    print(index_path.resolve())
    print(csv_path.resolve())
    print(quality_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
