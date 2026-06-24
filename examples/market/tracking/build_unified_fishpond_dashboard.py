from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECENT_HIGH_CSV = ROOT / "recent-high-fishpond.csv"
OUTPUT = ROOT / "unified-fishpond-dashboard.html"


def load_recent_high(limit: int = 120) -> list[dict[str, str]]:
    if not RECENT_HIGH_CSV.exists():
        return []
    with RECENT_HIGH_CSV.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))[:limit]


def build_data() -> dict[str, object]:
    recent_high = load_recent_high()
    ponds = [
        {
            "id": "recent-high",
            "name": "近期新高池",
            "status": "活跃池",
            "kind": "技术鱼塘",
            "updated": "2026-06-24",
            "thesis": "用近期创新高标的做第一层池塘，再用题材新鲜度、筹码干净度、分时强度和板块强度筛掉假突破。",
            "events": [
                "同花顺创新高榜用于快速建池。",
                "后续增强为 20 日、60 日、120 日、年内新高多周期分层。",
                "新高只代表市场投票，不代表可以直接追买。",
            ],
            "rules": [
                "优先：题材够新、筹码够干净、分时够强、板块有梯队。",
                "剔除：爆量长上影、连续加速末端、换手失控但封不住、板块逆势太弱。",
                "买点：突破后回踩不破，或放量突破后站稳均价线。",
            ],
            "columns": ["代码", "名称", "涨跌幅", "换手率", "最新价", "前期高点", "前期高点日期"],
            "rows": [
                [
                    item.get("股票代码", ""),
                    item.get("股票简称", ""),
                    item.get("涨跌幅", ""),
                    item.get("换手率", ""),
                    item.get("最新价", ""),
                    item.get("前期高点", ""),
                    item.get("前期高点日期", ""),
                ]
                for item in recent_high
            ],
        },
        {
            "id": "commercial-space",
            "name": "商业航天可回收火箭",
            "status": "观察池",
            "kind": "事件鱼塘",
            "updated": "2026-06-24",
            "thesis": "蓝箭、星河动力、天兵科技、深蓝航天等非上市火箭公司是事件源，A 股主要跟踪供应链映射和股权映射。",
            "events": [
                "蓝箭航天：朱雀三号、液氧甲烷、可重复使用火箭、科创板 IPO。",
                "星河动力：智神星一号可重复使用火箭首飞/复飞节奏。",
                "深蓝航天：酒泉子公司和火箭制造经营范围。",
                "航宇科技明确回应已配套蓝箭航天、星河动力、天兵科技等商业航天客户。",
            ],
            "rules": [
                "供应链证据强于股权传闻，优先跟踪已明确配套客户的标的。",
                "金风科技入股蓝箭线索保留，但未穿透前只放待核实。",
                "火箭事件升温 + A 股标的放量 + 板块有梯队，才从观察池升级。",
            ],
            "columns": ["分类", "代码", "名称", "状态", "逻辑", "触发", "失效"],
            "rows": [
                ["核心配套", "688239", "航宇科技", "保留", "已配套蓝箭、星河动力、天兵科技等民营火箭厂商。", "商业航天事件升温且放量突破。", "收入占比低或股价无承接。"],
                ["股权线索", "002202", "金风科技", "观察期", "市场线索称金风体系入股蓝箭，持股比例待核实。", "招股书/年报/工商穿透确认。", "无法确认持股或市场不认可。"],
                ["股权线索", "02208.HK", "金风科技H股", "观察期", "同一主体港股映射，A 股 002202 优先。", "AH 联动且蓝箭事件升温。", "港股无承接或 A 股不跟随。"],
                ["投资人映射", "600282", "南钢股份", "观察期", "星际荣耀早期融资曾披露南京钢铁参与认购，比例未披露。", "星际荣耀可重复使用火箭节点升温。", "钢铁主业拖累或无承接。"],
                ["投资人映射", "00656.HK", "复星国际", "观察期", "星际荣耀早期融资曾披露复星集团参与，比例未披露。", "星际荣耀重大事件叠加资本映射。", "港股平台弱，A 股交易意义低。"],
                ["国家队中军", "600118", "中国卫星", "保留", "卫星制造与空间基础设施中军。", "卫星互联网/国家队任务带动。", "航天军工退潮。"],
                ["结构件", "301005", "超捷股份", "保留", "结构件、紧固件弹性标的。", "火箭事件前资金提前放量。", "事件兑现后回落。"],
                ["高端材料", "688122", "西部超导", "保留", "钛合金、高温合金材料中军。", "航天材料池共振。", "材料线退潮。"],
            ],
        },
        {
            "id": "rubin-coolant",
            "name": "Rubin 液冷/冷却液",
            "status": "富矿池",
            "kind": "产业鱼塘",
            "updated": "2026-06-24",
            "thesis": "AI 硬件扩散到液冷和冷却液材料，重点看氟化液、有机氟、电子化学品是否持续放量。",
            "events": [
                "Rubin 和 AI 服务器液冷催化。",
                "巨化股份、新宙邦作为中军/弹性核心的承接。",
                "永和股份、三美股份等氟化工扩散观察。",
            ],
            "rules": [
                "巨化和新宙邦同步强，鱼塘质量提升。",
                "核心股放量跌破关键支撑且扩散断掉，降级。",
            ],
            "columns": ["分类", "代码", "名称", "状态", "逻辑", "触发", "失效"],
            "rows": [
                ["中军", "600160", "巨化股份", "保留", "氟化工容量中军。", "回踩承接或放量突破。", "放量跌破关键支撑。"],
                ["弹性", "300037", "新宙邦", "保留", "电子化学品/有机氟弹性。", "站稳关键位并放量。", "反抽无量或跌破支撑。"],
                ["扩散", "605020", "永和股份", "观察期", "氟化工一体化。", "核心走强后补涨。", "核心转弱且不承接。"],
                ["扩散", "603379", "三美股份", "观察期", "制冷剂/氟化工扩散。", "板块扩散时放量。", "冲高回落无承接。"],
            ],
        },
        {
            "id": "copper-foil",
            "name": "铜箔/铜资源映射",
            "status": "观察池",
            "kind": "映射鱼塘",
            "updated": "2026-06-24",
            "thesis": "铜冠铜箔高弹性核心和铜陵有色资源中军之间的长期映射链。当前需要重新确认承接。",
            "events": [
                "铜冠铜箔是否保持高成交辨识度。",
                "铜陵有色是否修复跌停后的承接。",
                "铜价和有色板块是否重新走强。",
            ],
            "rules": [
                "铜陵重新站回关键位并放量，才恢复观察强度。",
                "跌停后无修复，短线补涨逻辑失效。",
            ],
            "columns": ["分类", "代码", "名称", "状态", "逻辑", "触发", "失效"],
            "rows": [
                ["核心", "301217", "铜冠铜箔", "观察期", "铜箔/PCB 材料高弹性核心。", "高位分歧后重新转强。", "高位连续退潮。"],
                ["映射中军", "000630", "铜陵有色", "降级", "铜资源中军，铜箔资产映射。", "重新站回关键位并放量。", "跌停后无修复或继续破位。"],
            ],
        },
        {
            "id": "pcb-equipment",
            "name": "PCB设备/大族链",
            "status": "观察池",
            "kind": "子母映射",
            "updated": "2026-06-24",
            "thesis": "大族数控高弹性核心与大族激光平台映射，是子母/分拆映射模板链。",
            "events": [
                "大族数控是否保持高位辨识度。",
                "大族激光是否缩量止跌或放量修复。",
                "PCB、封测、电子设备方向是否继续扩散。",
            ],
            "rules": [
                "大族数控强，大族激光放量修复，鱼塘升级。",
                "两者同步放量下跌，鱼塘降级。",
            ],
            "columns": ["分类", "代码", "名称", "状态", "逻辑", "触发", "失效"],
            "rows": [
                ["核心", "301200", "大族数控", "保留", "PCB 设备高弹性核心。", "维持高位强度。", "高位退潮。"],
                ["映射平台", "002008", "大族激光", "观察期", "母公司/平台映射。", "缩量回踩后放量修复。", "持续放量下跌。"],
            ],
        },
    ]
    return {"ponds": ponds}


def main() -> None:
    data_json = json.dumps(build_data(), ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>统一鱼塘看板</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --panel: #fff;
      --soft: #f0f3f7;
      --text: #172033;
      --muted: #667085;
      --line: #d9dee7;
      --blue: #2563eb;
      --green: #0f8b4c;
      --amber: #b7791f;
      --red: #c2413a;
      --violet: #6d5bd0;
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    html {{ overflow-x: hidden; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); overflow-x: hidden; }}
    header {{ background: #111827; color: #fff; border-bottom: 4px solid #d33f2f; }}
    .header-inner {{ max-width: 1500px; margin: 0 auto; padding: 22px 18px; }}
    h1 {{ margin: 0; font-size: 26px; letter-spacing: 0; }}
    header p {{ margin: 8px 0 0; color: #cbd5e1; }}
    main {{ width: 100%; max-width: 1500px; margin: 0 auto; padding: 18px; display: grid; grid-template-columns: 310px minmax(0, 1fr); gap: 18px; }}
    main > *, .content, aside, section {{ min-width: 0; }}
    aside, section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: 0 8px 24px rgba(31, 41, 51, .08); }}
    aside {{ padding: 14px; align-self: start; position: sticky; top: 12px; }}
    .toolbar {{ display: grid; gap: 10px; margin-bottom: 14px; }}
    input, select {{ width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 10px; font-size: 14px; }}
    .pond-list {{ display: grid; gap: 8px; }}
    .pond-button {{ width: 100%; border: 1px solid var(--line); background: #fff; border-radius: 6px; padding: 10px; text-align: left; cursor: pointer; }}
    .pond-button.active {{ border-color: var(--blue); background: #eff6ff; }}
    .pond-title {{ display: flex; justify-content: space-between; gap: 8px; align-items: center; font-weight: 700; font-size: 14px; }}
    .pond-meta {{ margin-top: 5px; color: var(--muted); font-size: 12px; }}
    .content {{ display: grid; gap: 18px; }}
    .summary, .panel {{ padding: 16px; }}
    .summary-top {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 14px; min-width: 0; }}
    .summary-top > div:first-child {{ min-width: 0; }}
    h2 {{ margin: 0; font-size: 22px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 10px; font-size: 16px; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{ display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 700; white-space: nowrap; }}
    .rich {{ background: #e7f8ef; color: var(--green); }}
    .active {{ background: #eff6ff; color: var(--blue); }}
    .watch {{ background: #fff7e6; color: var(--amber); }}
    .keep {{ background: #e8f7ee; color: var(--green); }}
    .probation {{ background: #f1edff; color: var(--violet); }}
    .downgrade {{ background: #fff4df; color: var(--amber); }}
    .remove {{ background: #fff0ef; color: var(--red); }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
    .metric {{ background: var(--soft); border-radius: 8px; padding: 11px; min-height: 74px; }}
    .metric strong {{ display: block; font-size: 20px; margin-bottom: 4px; }}
    .metric span {{ color: var(--muted); font-size: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .note-list {{ margin: 0; padding-left: 18px; color: #344054; line-height: 1.65; font-size: 14px; }}
    .table-tools {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }}
    .table-tools input, .table-tools select {{ width: auto; min-width: 180px; }}
    .table-wrap {{ width: 100%; max-width: 100%; overflow: auto; border: 1px solid var(--line); border-radius: 8px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 980px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 10px; text-align: left; vertical-align: top; font-size: 13px; }}
    th {{ background: #f8fafc; color: #334155; position: sticky; top: 0; }}
    tbody tr {{ cursor: pointer; }}
    tbody tr:hover {{ background: #f8fbff; }}
    tr:last-child td {{ border-bottom: 0; }}
    .code {{ font-family: Consolas, "Courier New", monospace; color: #475569; white-space: nowrap; }}
    .modal-backdrop {{ position: fixed; inset: 0; display: none; align-items: center; justify-content: center; padding: 18px; background: rgba(15, 23, 42, .46); z-index: 20; }}
    .modal-backdrop.open {{ display: flex; }}
    .modal {{ width: min(1120px, 100%); max-height: min(92vh, 860px); overflow: auto; background: #fff; border-radius: 8px; border: 1px solid var(--line); box-shadow: 0 22px 70px rgba(15, 23, 42, .30); }}
    .modal-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 16px; border-bottom: 1px solid var(--line); }}
    .modal-title {{ font-size: 20px; font-weight: 800; }}
    .modal-subtitle {{ margin-top: 4px; color: var(--muted); font-size: 13px; }}
    .modal-close {{ border: 1px solid var(--line); background: #fff; border-radius: 6px; padding: 8px 10px; cursor: pointer; }}
    .quote-grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; padding: 16px; }}
    .quote-item {{ background: var(--soft); border-radius: 8px; padding: 10px; }}
    .quote-item b {{ display: block; font-size: 18px; margin-bottom: 3px; }}
    .quote-item span {{ color: var(--muted); font-size: 12px; }}
    .chart-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; padding: 0 16px 16px; }}
    .chart-card {{ border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 0; }}
    .chart-card h4 {{ margin: 0 0 10px; font-size: 15px; }}
    canvas {{ width: 100%; height: 280px; display: block; }}
    .modal-note {{ padding: 0 16px 16px; color: var(--muted); font-size: 13px; line-height: 1.6; }}
    @media (max-width: 980px) {{
      main {{ grid-template-columns: 1fr; padding: 12px; }}
      .header-inner {{ padding: 18px 12px; }}
      .summary-top {{ display: grid; }}
      aside {{ position: static; }}
      .metrics, .grid {{ grid-template-columns: 1fr; }}
      .table-tools input, .table-tools select {{ width: 100%; }}
      .quote-grid, .chart-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>统一鱼塘看板</h1>
    <p>把近期新高池和主题鱼塘放在同一页面：先看鱼塘质量，再看标的、触发、失效和观察状态。</p>
  </header>
  <main>
    <aside>
      <div class="toolbar">
        <input id="pondSearch" type="search" placeholder="搜索鱼塘/标的/代码">
        <select id="statusFilter">
          <option value="all">全部状态</option>
          <option value="富矿池">富矿池</option>
          <option value="活跃池">活跃池</option>
          <option value="观察池">观察池</option>
        </select>
      </div>
      <div id="pondList" class="pond-list"></div>
    </aside>
    <div class="content">
      <section class="summary">
        <div class="summary-top">
          <div>
            <h2 id="pondName"></h2>
            <p id="pondThesis" style="margin:8px 0 0;color:var(--muted);line-height:1.55;"></p>
          </div>
          <div id="pondTags" class="tags"></div>
        </div>
        <div class="metrics">
          <div class="metric"><strong id="metricStatus"></strong><span>鱼塘质量</span></div>
          <div class="metric"><strong id="metricKind"></strong><span>鱼塘类型</span></div>
          <div class="metric"><strong id="metricRows"></strong><span>跟踪标的</span></div>
          <div class="metric"><strong id="metricUpdated"></strong><span>更新时间</span></div>
        </div>
      </section>
      <div class="grid">
        <section class="panel">
          <h3>核心事件</h3>
          <ul id="eventList" class="note-list"></ul>
        </section>
        <section class="panel">
          <h3>触发与失效</h3>
          <ul id="ruleList" class="note-list"></ul>
        </section>
      </div>
      <section class="panel">
        <h3>标的列表</h3>
        <div class="table-tools">
          <input id="tableSearch" type="search" placeholder="搜索表格">
          <select id="turnoverFilter">
            <option value="all">全部换手</option>
            <option value="low">换手≤5%</option>
            <option value="mid">5% < 换手≤15%</option>
            <option value="high">换手>15%</option>
          </select>
        </div>
        <div class="table-wrap">
          <table>
            <thead id="tableHead"></thead>
            <tbody id="tableBody"></tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
  <div id="stockModal" class="modal-backdrop">
    <div class="modal">
      <div class="modal-head">
        <div>
          <div id="modalTitle" class="modal-title">标的详情</div>
          <div id="modalSubtitle" class="modal-subtitle"></div>
        </div>
        <button id="modalClose" class="modal-close" type="button">关闭</button>
      </div>
      <div id="quoteGrid" class="quote-grid"></div>
      <div class="chart-grid">
        <div class="chart-card">
          <h4>分时概览</h4>
          <canvas id="minuteCanvas" width="520" height="280"></canvas>
        </div>
        <div class="chart-card">
          <h4>日K走势</h4>
          <canvas id="dailyCanvas" width="520" height="280"></canvas>
        </div>
      </div>
      <div id="modalNote" class="modal-note"></div>
    </div>
  </div>
  <script>
    const data = {data_json};
    const state = {{ selected: data.ponds[0].id, pondSearch: "", status: "all", tableSearch: "", turnover: "all" }};
    const els = {{
      pondSearch: document.getElementById("pondSearch"),
      statusFilter: document.getElementById("statusFilter"),
      pondList: document.getElementById("pondList"),
      pondName: document.getElementById("pondName"),
      pondThesis: document.getElementById("pondThesis"),
      pondTags: document.getElementById("pondTags"),
      metricStatus: document.getElementById("metricStatus"),
      metricKind: document.getElementById("metricKind"),
      metricRows: document.getElementById("metricRows"),
      metricUpdated: document.getElementById("metricUpdated"),
      eventList: document.getElementById("eventList"),
      ruleList: document.getElementById("ruleList"),
      tableHead: document.getElementById("tableHead"),
      tableBody: document.getElementById("tableBody"),
      tableSearch: document.getElementById("tableSearch"),
      turnoverFilter: document.getElementById("turnoverFilter"),
      stockModal: document.getElementById("stockModal"),
      modalTitle: document.getElementById("modalTitle"),
      modalSubtitle: document.getElementById("modalSubtitle"),
      modalClose: document.getElementById("modalClose"),
      quoteGrid: document.getElementById("quoteGrid"),
      minuteCanvas: document.getElementById("minuteCanvas"),
      dailyCanvas: document.getElementById("dailyCanvas"),
      modalNote: document.getElementById("modalNote")
    }};
    function cls(status) {{
      if (status === "富矿池" || status === "保留") return "rich";
      if (status === "活跃池") return "active";
      if (status === "观察池") return "watch";
      if (status === "观察期") return "probation";
      if (status === "降级") return "downgrade";
      if (status === "剔除") return "remove";
      return "active";
    }}
    function pondMatches(pond) {{
      const q = state.pondSearch.trim().toLowerCase();
      const statusOk = state.status === "all" || pond.status === state.status;
      if (!statusOk) return false;
      if (!q) return true;
      return JSON.stringify(pond).toLowerCase().includes(q);
    }}
    function filteredPonds() {{ return data.ponds.filter(pondMatches); }}
    function selectedPond() {{ return data.ponds.find((p) => p.id === state.selected) || filteredPonds()[0] || data.ponds[0]; }}
    function renderPondList() {{
      const list = filteredPonds();
      if (!list.some((p) => p.id === state.selected) && list[0]) state.selected = list[0].id;
      els.pondList.innerHTML = list.map((pond) => `
        <button class="pond-button ${{pond.id === state.selected ? "active" : ""}}" data-id="${{pond.id}}">
          <div class="pond-title"><span>${{pond.name}}</span><span class="tag ${{cls(pond.status)}}">${{pond.status}}</span></div>
          <div class="pond-meta">${{pond.kind}} · ${{pond.rows.length}} 个标的</div>
        </button>
      `).join("");
      els.pondList.querySelectorAll("button").forEach((button) => {{
        button.addEventListener("click", () => {{ state.selected = button.dataset.id; state.tableSearch = ""; els.tableSearch.value = ""; render(); }});
      }});
    }}
    function renderTable(pond) {{
      els.turnoverFilter.style.display = pond.id === "recent-high" ? "" : "none";
      els.tableHead.innerHTML = `<tr>${{pond.columns.map((col) => `<th>${{col}}</th>`).join("")}}</tr>`;
      const q = state.tableSearch.trim().toLowerCase();
      const rows = pond.rows.filter((row) => {{
        let ok = !q || row.join(" ").toLowerCase().includes(q);
        if (pond.id === "recent-high") {{
          const turnover = parseFloat(row[3]);
          if (state.turnover === "low") ok = ok && turnover <= 5;
          if (state.turnover === "mid") ok = ok && turnover > 5 && turnover <= 15;
          if (state.turnover === "high") ok = ok && turnover > 15;
        }}
        return ok;
      }});
      els.tableBody.innerHTML = rows.map((row) => `<tr data-row='${{JSON.stringify(row).replaceAll("'", "&apos;")}}'>${{row.map((cell, idx) => `<td class="${{idx === 0 ? "code" : ""}}">${{cell}}</td>`).join("")}}</tr>`).join("");
      els.tableBody.querySelectorAll("tr").forEach((tr) => {{
        tr.addEventListener("click", () => openStockModal(JSON.parse(tr.dataset.row.replaceAll("&apos;", "'"))));
      }});
    }}
    function renderSelected() {{
      const pond = selectedPond();
      els.pondName.textContent = pond.name;
      els.pondThesis.textContent = pond.thesis;
      els.pondTags.innerHTML = `<span class="tag ${{cls(pond.status)}}">${{pond.status}}</span><span class="tag active">${{pond.kind}}</span>`;
      els.metricStatus.textContent = pond.status;
      els.metricKind.textContent = pond.kind;
      els.metricRows.textContent = pond.rows.length;
      els.metricUpdated.textContent = pond.updated;
      els.eventList.innerHTML = pond.events.map((item) => `<li>${{item}}</li>`).join("");
      els.ruleList.innerHTML = pond.rules.map((item) => `<li>${{item}}</li>`).join("");
      renderTable(pond);
    }}
    function render() {{ renderPondList(); renderSelected(); }}
    els.pondSearch.addEventListener("input", (event) => {{ state.pondSearch = event.target.value; render(); }});
    els.statusFilter.addEventListener("change", (event) => {{ state.status = event.target.value; render(); }});
    els.tableSearch.addEventListener("input", (event) => {{ state.tableSearch = event.target.value; renderSelected(); }});
    els.turnoverFilter.addEventListener("change", (event) => {{ state.turnover = event.target.value; renderSelected(); }});
    let stockRefreshTimer = null;
    let activeStock = null;
    function closeStockModal() {{
      els.stockModal.classList.remove("open");
      if (stockRefreshTimer) window.clearInterval(stockRefreshTimer);
      stockRefreshTimer = null;
      activeStock = null;
    }}
    els.modalClose.addEventListener("click", closeStockModal);
    els.stockModal.addEventListener("click", (event) => {{ if (event.target === els.stockModal) closeStockModal(); }});

    function normalizeCode(raw) {{
      const text = String(raw || "").trim();
      const six = text.match(/\\d{{6}}/);
      if (!six) return null;
      const code = six[0];
      const market = code.startsWith("6") ? "sh" : "sz";
      const secidMarket = code.startsWith("6") ? "1" : "0";
      return {{ code, market, tencent: market + code, secid: secidMarket + "." + code }};
    }}

    async function openStockModal(row) {{
      const codeInfo = normalizeCode(row[0]);
      const name = row[1] || row[2] || "";
      if (stockRefreshTimer) window.clearInterval(stockRefreshTimer);
      stockRefreshTimer = null;
      activeStock = null;
      els.stockModal.classList.add("open");
      els.modalTitle.textContent = `${{name || "标的"}} ${{row[0] || ""}}`;
      els.modalSubtitle.textContent = "正在加载行情图表...";
      els.quoteGrid.innerHTML = "";
      els.modalNote.textContent = "";
      clearCanvas(els.minuteCanvas);
      clearCanvas(els.dailyCanvas);
      if (!codeInfo) {{
        els.modalSubtitle.textContent = "该行不是可识别的 A 股代码，暂不支持图表。";
        els.modalNote.textContent = "可识别格式包括 000001、600000、000001.XSHE、600000.XSHG 等。";
        return;
      }}
      activeStock = {{ codeInfo, fallbackName: name }};
      await refreshStockModal(true);
      stockRefreshTimer = window.setInterval(() => refreshStockModal(false), isMarketOpen() ? 15000 : 60000);
    }}

    async function refreshStockModal(showLoading) {{
      if (!activeStock) return;
      const {{ codeInfo, fallbackName }} = activeStock;
      if (showLoading) els.modalSubtitle.textContent = "正在加载行情图表...";
      try {{
        const [quote, minute, daily] = await Promise.all([
          fetchTencentQuote(codeInfo.tencent),
          fetchEastmoneyMinute(codeInfo.secid),
          fetchEastmoneyDaily(codeInfo.secid)
        ]);
        els.modalTitle.textContent = `${{quote.name || name}} ${{codeInfo.code}}`;
        els.modalSubtitle.textContent = quote.time ? `行情时间：${{quote.time}}` : "行情时间：-";
        renderQuote(quote);
        drawLineChart(els.minuteCanvas, minute, "price", quote.preClose);
        drawKChart(els.dailyCanvas, daily);
        els.modalNote.textContent = `提示：弹窗打开期间会自动刷新。交易时间约 15 秒刷新一次，非交易时间约 60 秒刷新一次。最新刷新：${{new Date().toLocaleTimeString("zh-CN", {{ hour12: false }})}}。`;
      }} catch (error) {{
        els.modalSubtitle.textContent = "行情接口加载失败";
        els.modalNote.textContent = String(error && error.message ? error.message : error);
      }}
    }}

    function isMarketOpen() {{
      const now = new Date();
      const day = now.getDay();
      if (day === 0 || day === 6) return false;
      const minutes = now.getHours() * 60 + now.getMinutes();
      return (minutes >= 9 * 60 + 25 && minutes <= 11 * 60 + 30) || (minutes >= 13 * 60 && minutes <= 15 * 60 + 5);
    }}

    async function fetchTencentQuote(symbol) {{
      const response = await fetch(`https://qt.gtimg.cn/q=${{symbol}}`);
      const buffer = await response.arrayBuffer();
      let text = "";
      try {{
        text = new TextDecoder("gb18030").decode(buffer);
      }} catch (error) {{
        text = new TextDecoder("gbk").decode(buffer);
      }}
      const body = text.split("=")[1]?.replace(/^"|"；?;?$/g, "").replace(/";?$/, "") || "";
      const arr = body.split("~");
      return {{
        name: arr[1],
        code: arr[2],
        price: Number(arr[3]),
        preClose: Number(arr[4]),
        open: Number(arr[5]),
        high: Number(arr[33]),
        low: Number(arr[34]),
        change: Number(arr[31]),
        pct: Number(arr[32]),
        amount: Number(arr[37]),
        volume: Number(arr[36]),
        turnover: Number(arr[38]),
        time: arr[30]
      }};
    }}

    async function fetchEastmoneyMinute(secid) {{
      const url = `https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid=${{secid}}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11&fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&iscca=0&ndays=1`;
      const data = await (await fetch(url)).json();
      const trends = data?.data?.trends || [];
      return trends.map((item) => {{
        const p = item.split(",");
        return {{ time: p[0], price: Number(p[2]), avg: Number(p[3]), volume: Number(p[5]) }};
      }}).filter((item) => Number.isFinite(item.price));
    }}

    async function fetchEastmoneyDaily(secid) {{
      const url = `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=${{secid}}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20250101&end=20500101&lmt=80`;
      const data = await (await fetch(url)).json();
      const klines = data?.data?.klines || [];
      return klines.map((item) => {{
        const p = item.split(",");
        return {{ date: p[0], open: Number(p[1]), close: Number(p[2]), high: Number(p[3]), low: Number(p[4]), volume: Number(p[5]) }};
      }}).filter((item) => Number.isFinite(item.close));
    }}

    function renderQuote(q) {{
      const items = [
        ["现价", q.price],
        ["涨跌幅", `${{q.pct || 0}}%`],
        ["今开", q.open],
        ["最高", q.high],
        ["最低", q.low],
        ["昨收", q.preClose],
        ["成交额", q.amount ? `${{(q.amount / 10000).toFixed(2)}} 亿` : "-"],
        ["换手", Number.isFinite(q.turnover) ? `${{q.turnover}}%` : "-"]
      ];
      els.quoteGrid.innerHTML = items.map(([label, value]) => `<div class="quote-item"><b>${{value ?? "-"}}</b><span>${{label}}</span></div>`).join("");
    }}

    function clearCanvas(canvas) {{
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }}

    function drawLineChart(canvas, data, key, ref) {{
      const ctx = canvas.getContext("2d");
      clearCanvas(canvas);
      const w = canvas.width, h = canvas.height, pad = 28;
      if (!data.length) return drawEmpty(ctx, w, h, "暂无分时数据");
      const values = data.map((d) => d[key]).filter(Number.isFinite);
      if (Number.isFinite(ref)) values.push(ref);
      const min = Math.min(...values), max = Math.max(...values);
      const span = max - min || 1;
      ctx.strokeStyle = "#d9dee7"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(pad, h - pad); ctx.lineTo(w - pad, h - pad); ctx.stroke();
      if (Number.isFinite(ref)) {{
        const y = h - pad - ((ref - min) / span) * (h - pad * 2);
        ctx.strokeStyle = "#cbd5e1"; ctx.setLineDash([5, 5]); ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(w - pad, y); ctx.stroke(); ctx.setLineDash([]);
      }}
      ctx.strokeStyle = "#2563eb"; ctx.lineWidth = 2; ctx.beginPath();
      data.forEach((d, i) => {{
        const x = pad + (i / Math.max(data.length - 1, 1)) * (w - pad * 2);
        const y = h - pad - ((d[key] - min) / span) * (h - pad * 2);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }});
      ctx.stroke();
      drawAxisText(ctx, min, max, pad, w, h);
    }}

    function drawKChart(canvas, data) {{
      const ctx = canvas.getContext("2d");
      clearCanvas(canvas);
      const w = canvas.width, h = canvas.height, pad = 28;
      if (!data.length) return drawEmpty(ctx, w, h, "暂无日K数据");
      const lows = data.map((d) => d.low), highs = data.map((d) => d.high);
      const min = Math.min(...lows), max = Math.max(...highs), span = max - min || 1;
      const step = (w - pad * 2) / data.length;
      ctx.strokeStyle = "#d9dee7"; ctx.beginPath(); ctx.moveTo(pad, h - pad); ctx.lineTo(w - pad, h - pad); ctx.stroke();
      data.forEach((d, i) => {{
        const x = pad + i * step + step / 2;
        const yHigh = h - pad - ((d.high - min) / span) * (h - pad * 2);
        const yLow = h - pad - ((d.low - min) / span) * (h - pad * 2);
        const yOpen = h - pad - ((d.open - min) / span) * (h - pad * 2);
        const yClose = h - pad - ((d.close - min) / span) * (h - pad * 2);
        const up = d.close >= d.open;
        ctx.strokeStyle = up ? "#c2413a" : "#0f8b4c";
        ctx.fillStyle = up ? "#c2413a" : "#0f8b4c";
        ctx.beginPath(); ctx.moveTo(x, yHigh); ctx.lineTo(x, yLow); ctx.stroke();
        const top = Math.min(yOpen, yClose), height = Math.max(Math.abs(yClose - yOpen), 1);
        ctx.fillRect(x - Math.max(step * .3, 1), top, Math.max(step * .6, 2), height);
      }});
      drawAxisText(ctx, min, max, pad, w, h);
    }}

    function drawAxisText(ctx, min, max, pad, w, h) {{
      ctx.fillStyle = "#667085"; ctx.font = "12px Arial";
      ctx.fillText(String(max.toFixed ? max.toFixed(2) : max), 4, pad);
      ctx.fillText(String(min.toFixed ? min.toFixed(2) : min), 4, h - pad);
    }}

    function drawEmpty(ctx, w, h, text) {{
      ctx.fillStyle = "#667085"; ctx.font = "14px Microsoft YaHei, Arial"; ctx.textAlign = "center"; ctx.fillText(text, w / 2, h / 2);
      ctx.textAlign = "left";
    }}
    render();
  </script>
</body>
</html>
"""
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"generated {OUTPUT}")


if __name__ == "__main__":
    main()
