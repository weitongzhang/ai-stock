from __future__ import annotations

from pathlib import Path

import akshare as ak


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "recent-high-fishpond.csv"
HTML_PATH = ROOT / "recent-high-fishpond.html"


def cell(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    df = ak.stock_rank_cxg_ths()
    columns = ["股票代码", "股票简称", "涨跌幅", "换手率", "最新价", "前期高点", "前期高点日期"]
    df = df[columns].copy()
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

    rows = []
    for row in df.head(100).itertuples(index=False):
        rows.append(
            "<tr>"
            f"<td>{cell(row.股票代码)}</td>"
            f"<td>{cell(row.股票简称)}</td>"
            f"<td>{cell(row.涨跌幅)}</td>"
            f"<td>{cell(row.换手率)}</td>"
            f"<td>{cell(row.最新价)}</td>"
            f"<td>{cell(row.前期高点)}</td>"
            f"<td>{cell(row.前期高点日期)}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>近期新高鱼塘</title>
  <style>
    body {{ margin: 0; background: #f6f7f9; color: #172033; font-family: "Microsoft YaHei", Arial, sans-serif; }}
    header {{ background: #111827; color: #fff; padding: 22px 28px; border-bottom: 4px solid #d33f2f; }}
    h1 {{ margin: 0; font-size: 26px; letter-spacing: 0; }}
    header p {{ margin: 8px 0 0; color: #cbd5e1; }}
    main {{ max-width: 1360px; margin: 0 auto; padding: 18px; display: grid; gap: 16px; }}
    section {{ background: #fff; border: 1px solid #d9dee7; border-radius: 8px; box-shadow: 0 8px 24px rgba(31, 41, 51, .08); padding: 16px; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
    .card {{ background: #f0f3f7; border-radius: 8px; padding: 12px; min-height: 78px; }}
    .card b {{ display: block; font-size: 22px; margin-bottom: 5px; }}
    .card span, .muted {{ color: #667085; font-size: 13px; }}
    .rules {{ line-height: 1.72; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    input, select {{ border: 1px solid #d9dee7; border-radius: 6px; padding: 10px; font-size: 14px; }}
    input {{ min-width: 260px; }}
    .wrap {{ overflow: auto; border: 1px solid #d9dee7; border-radius: 8px; }}
    table {{ width: 100%; min-width: 880px; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #d9dee7; padding: 9px 10px; text-align: left; font-size: 13px; }}
    th {{ background: #f8fafc; color: #334155; position: sticky; top: 0; }}
    tr:last-child td {{ border-bottom: 0; }}
    .good {{ color: #0f8b4c; font-weight: 700; }}
    .bad {{ color: #c2413a; font-weight: 700; }}
    @media (max-width: 900px) {{ .cards {{ grid-template-columns: 1fr; }} input {{ min-width: 100%; }} }}
  </style>
</head>
<body>
  <header>
    <h1>近期新高鱼塘</h1>
    <p>用近期创新高标的做第一层池塘，再用题材新鲜度、筹码干净度、分时强度和板块强度筛掉假突破。</p>
  </header>
  <main>
    <section>
      <div class="cards">
        <div class="card"><b>{len(df)}</b><span>当前创新高标的</span></div>
        <div class="card"><b>前100</b><span>页面展示数量</span></div>
        <div class="card"><b>20/60/120</b><span>后续增强为多周期新高</span></div>
        <div class="card"><b>只试不追</b><span>突破后等回踩确认</span></div>
      </div>
    </section>
    <section class="rules">
      <b>使用规则：</b>
      近期新高只负责建池，不直接买入。优先看“题材够新、筹码够干净、分时够强、板块有梯队”的票；
      剔除爆量长上影、板块逆势弱、连续加速末端、换手失控但封不住的票。
      <div class="muted">数据源：AKShare 同花顺创新高榜；生成文件：recent-high-fishpond.csv。</div>
    </section>
    <section>
      <div class="toolbar">
        <input id="q" placeholder="搜索代码/名称">
        <select id="turnover">
          <option value="all">全部换手</option>
          <option value="low">换手≤5%</option>
          <option value="mid">5% < 换手≤15%</option>
          <option value="high">换手>15%</option>
        </select>
      </div>
    </section>
    <section>
      <div class="wrap">
        <table id="tbl">
          <thead>
            <tr>
              <th>代码</th>
              <th>名称</th>
              <th>涨跌幅%</th>
              <th>换手率%</th>
              <th>最新价</th>
              <th>前期高点</th>
              <th>前期高点日期</th>
            </tr>
          </thead>
          <tbody>
            {"".join(rows)}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const q = document.getElementById("q");
    const sel = document.getElementById("turnover");
    const rows = [...document.querySelectorAll("#tbl tbody tr")];
    function filterRows() {{
      const text = q.value.trim().toLowerCase();
      const bucket = sel.value;
      rows.forEach((row) => {{
        const haystack = row.innerText.toLowerCase();
        const turnover = parseFloat(row.children[3].innerText);
        let ok = !text || haystack.includes(text);
        if (bucket === "low") ok = ok && turnover <= 5;
        if (bucket === "mid") ok = ok && turnover > 5 && turnover <= 15;
        if (bucket === "high") ok = ok && turnover > 15;
        row.style.display = ok ? "" : "none";
      }});
    }}
    q.addEventListener("input", filterRows);
    sel.addEventListener("change", filterRows);
  </script>
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"generated {HTML_PATH} with {len(df)} rows")


if __name__ == "__main__":
    main()
