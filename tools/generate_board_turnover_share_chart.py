"""Generate ChiNext and STAR Market turnover-share data and chart.

The calculation uses broad-market indices whose turnover covers each board:

- ChiNext Composite (399102.XSHE)
- STAR Composite (000680.XSHG)
- Shanghai Composite (000001.XSHG)
- Shenzhen Composite (399106.XSHE)

Share = board index turnover / (Shanghai Composite turnover + Shenzhen Composite turnover).
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path


INDEXES = {
    "chinext": "399102.XSHE",
    "star": "000680.XSHG",
    "shanghai": "000001.XSHG",
    "shenzhen": "399106.XSHE",
}


def subtract_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def fetch_index_ohlcs(run_py: Path, symbol: str, limit: int) -> dict[date, float]:
    command = [
        sys.executable,
        str(run_py),
        "index-ohlcs",
        "--index",
        symbol,
        "--span",
        "DAY1",
        "--limit",
        str(limit),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    payload = json.loads(result.stdout)
    return {
        datetime.fromtimestamp(item["otm"] / 1000).date(): float(item["t"])
        for item in payload["ohlcs"]
        if item.get("t") is not None
    }


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date",
        "a_share_turnover_yi",
        "chinext_turnover_yi",
        "star_turnover_yi",
        "chinext_share_pct",
        "star_share_pct",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def configure_chinese_font() -> None:
    import matplotlib

    matplotlib.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False


def write_chart(rows: list[dict[str, object]], output: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import PercentFormatter
    except ModuleNotFoundError:
        write_chart_pillow(rows, output)
        return

    configure_chinese_font()
    dates = [datetime.strptime(str(row["date"]), "%Y-%m-%d") for row in rows]
    chinext = [float(row["chinext_share_pct"]) / 100 for row in rows]
    star = [float(row["star_share_pct"]) / 100 for row in rows]

    fig, left = plt.subplots(figsize=(14, 7.5), dpi=160)
    right = left.twinx()

    red = "#c84b45"
    green = "#83a942"
    left.plot(dates, chinext, color=red, linewidth=2.2, label="创业板成交额占比")
    right.plot(dates, star, color=green, linewidth=2.2, label="科创板成交额占比")

    left.set_title("最近三个月创业板、科创板成交额占全A比例", fontsize=17, pad=18)
    left.set_ylabel("创业板成交额占比", color=red)
    right.set_ylabel("科创板成交额占比", color=green)
    left.yaxis.set_major_formatter(PercentFormatter(1))
    right.yaxis.set_major_formatter(PercentFormatter(1))
    left.grid(axis="y", color="#d7d7d7", linewidth=0.8)
    left.spines[["top", "right"]].set_visible(False)
    right.spines[["top", "left"]].set_visible(False)

    step = max(1, len(dates) // 12)
    left.set_xticks(dates[::step])
    left.set_xticklabels([item.strftime("%m-%d") for item in dates[::step]], rotation=45, ha="right")

    latest_date = dates[-1]
    left.annotate(
        f"创业板 {chinext[-1]:.2%}",
        xy=(latest_date, chinext[-1]),
        xytext=(-125, 28),
        textcoords="offset points",
        color=red,
        arrowprops={"arrowstyle": "->", "color": red},
    )
    right.annotate(
        f"科创板 {star[-1]:.2%}",
        xy=(latest_date, star[-1]),
        xytext=(-125, -38),
        textcoords="offset points",
        color=green,
        arrowprops={"arrowstyle": "->", "color": green},
    )

    lines = left.get_lines() + right.get_lines()
    left.legend(lines, [line.get_label() for line in lines], loc="upper left", frameon=False)
    fig.text(
        0.01,
        0.01,
        "口径：创业板综/科创综指成交额 ÷（上证综指成交额 + 深证综指成交额）",
        fontsize=9,
        color="#666666",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def write_chart_pillow(rows: list[dict[str, object]], output: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1800, 960
    margin_left, margin_right, margin_top, margin_bottom = 145, 145, 110, 150
    chart_left, chart_right = margin_left, width - margin_right
    chart_top, chart_bottom = margin_top, height - margin_bottom
    chart_width, chart_height = chart_right - chart_left, chart_bottom - chart_top

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/simhei.ttf")
    title_font = ImageFont.truetype(str(font_path), 38)
    label_font = ImageFont.truetype(str(font_path), 23)
    small_font = ImageFont.truetype(str(font_path), 19)

    chinext = [float(row["chinext_share_pct"]) for row in rows]
    star = [float(row["star_share_pct"]) for row in rows]
    left_max = max(35.0, (int(max(chinext) / 5) + 2) * 5.0)
    right_max = max(20.0, (int(max(star) / 5) + 2) * 5.0)
    red, green, grid = "#c84b45", "#83a942", "#d3d3d3"

    def x_position(index: int) -> float:
        return chart_left + index / max(1, len(rows) - 1) * chart_width

    def y_position(value: float, maximum: float) -> float:
        return chart_bottom - value / maximum * chart_height

    title = "最近三个月创业板、科创板成交额占全A比例"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width - (title_box[2] - title_box[0])) / 2, 35), title, fill="#222222", font=title_font)

    for tick in range(0, 8):
        ratio = tick / 7
        y = chart_bottom - ratio * chart_height
        draw.line((chart_left, y, chart_right, y), fill=grid, width=2)
        left_label = f"{left_max * ratio:.0f}%"
        right_label = f"{right_max * ratio:.0f}%"
        draw.text((chart_left - 75, y - 12), left_label, fill=red, font=small_font)
        draw.text((chart_right + 15, y - 12), right_label, fill=green, font=small_font)

    draw.line((chart_left, chart_top, chart_left, chart_bottom), fill="#777777", width=2)
    draw.line((chart_right, chart_top, chart_right, chart_bottom), fill="#777777", width=2)
    draw.line((chart_left, chart_bottom, chart_right, chart_bottom), fill="#777777", width=2)

    chinext_points = [(x_position(i), y_position(value, left_max)) for i, value in enumerate(chinext)]
    star_points = [(x_position(i), y_position(value, right_max)) for i, value in enumerate(star)]
    draw.line(chinext_points, fill=red, width=5, joint="curve")
    draw.line(star_points, fill=green, width=5, joint="curve")

    step = max(1, len(rows) // 12)
    for index in range(0, len(rows), step):
        date_label = str(rows[index]["date"])[5:]
        x = x_position(index)
        draw.line((x, chart_bottom, x, chart_bottom + 8), fill="#777777", width=2)
        draw.text((x - 28, chart_bottom + 18), date_label, fill="#444444", font=small_font)

    draw.line((chart_left + 25, chart_top + 30, chart_left + 85, chart_top + 30), fill=red, width=5)
    draw.text((chart_left + 100, chart_top + 15), "创业板成交额占比", fill=red, font=label_font)
    draw.line((chart_left + 360, chart_top + 30, chart_left + 420, chart_top + 30), fill=green, width=5)
    draw.text((chart_left + 435, chart_top + 15), "科创板成交额占比", fill=green, font=label_font)

    latest_x = x_position(len(rows) - 1)
    latest_chinext_y = y_position(chinext[-1], left_max)
    latest_star_y = y_position(star[-1], right_max)
    draw.ellipse((latest_x - 7, latest_chinext_y - 7, latest_x + 7, latest_chinext_y + 7), fill=red)
    draw.ellipse((latest_x - 7, latest_star_y - 7, latest_x + 7, latest_star_y + 7), fill=green)
    draw.text(
        (latest_x - 235, latest_chinext_y - 45),
        f"创业板 {chinext[-1]:.2f}%",
        fill=red,
        font=label_font,
    )
    draw.text(
        (latest_x - 235, latest_star_y + 15),
        f"科创板 {star[-1]:.2f}%",
        fill=green,
        font=label_font,
    )

    note = "口径：创业板综/科创综指成交额 ÷（上证综指成交额 + 深证综指成交额）"
    draw.text((chart_left, height - 48), note, fill="#666666", font=small_font)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=3)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("examples/market/board-turnover-share"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    run_py = root / "skills" / "market-data" / "ftshare-market-data" / "run.py"
    series = {name: fetch_index_ohlcs(run_py, symbol, args.limit) for name, symbol in INDEXES.items()}

    latest_common = min(max(values) for values in series.values())
    start_date = subtract_months(latest_common, args.months)
    common_dates = sorted(set.intersection(*(set(values) for values in series.values())))

    rows: list[dict[str, object]] = []
    for trade_date in common_dates:
        if trade_date < start_date or trade_date > latest_common:
            continue
        total = series["shanghai"][trade_date] + series["shenzhen"][trade_date]
        rows.append(
            {
                "date": trade_date.isoformat(),
                "a_share_turnover_yi": round(total / 100_000_000, 2),
                "chinext_turnover_yi": round(series["chinext"][trade_date] / 100_000_000, 2),
                "star_turnover_yi": round(series["star"][trade_date] / 100_000_000, 2),
                "chinext_share_pct": round(series["chinext"][trade_date] / total * 100, 4),
                "star_share_pct": round(series["star"][trade_date] / total * 100, 4),
            }
        )

    if not rows:
        raise RuntimeError("No overlapping index turnover data returned.")

    stem = f"{rows[0]['date']}_{rows[-1]['date']}-board-turnover-share"
    csv_path = args.out_dir / f"{stem}.csv"
    png_path = args.out_dir / f"{stem}.png"
    write_csv(rows, csv_path)
    write_chart(rows, png_path)

    latest = rows[-1]
    print(
        json.dumps(
            {
                "rows": len(rows),
                "latest": latest,
                "csv": str(csv_path),
                "png": str(png_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
