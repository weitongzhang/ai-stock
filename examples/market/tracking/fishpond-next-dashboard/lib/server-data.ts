import fs from "node:fs";
import path from "node:path";
import { themePonds } from "./fishpond-data";
import type { Fishpond, RecentHighRow } from "./types";

const trackingRoot = path.resolve(process.cwd(), "..");

function parseCsvLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      quoted = !quoted;
    } else if (ch === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += ch;
    }
  }
  values.push(current);
  return values.map((value) => value.trim());
}

export function readRecentHighRows(limit = 160): RecentHighRow[] {
  const csvPath = path.join(trackingRoot, "recent-high-fishpond.csv");
  if (!fs.existsSync(csvPath)) return [];
  const text = fs.readFileSync(csvPath, "utf8").replace(/^\uFEFF/, "");
  const lines = text.split(/\r?\n/).filter(Boolean);
  const headers = parseCsvLine(lines[0] ?? "");
  return lines.slice(1, limit + 1).map((line) => {
    const values = parseCsvLine(line);
    const item = Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
    return {
      code: item["股票代码"] ?? "",
      name: item["股票简称"] ?? "",
      pct: item["涨跌幅"] ?? "",
      turnover: item["换手率"] ?? "",
      price: item["最新价"] ?? "",
      previousHigh: item["前期高点"] ?? "",
      previousHighDate: item["前期高点日期"] ?? ""
    };
  });
}

export function getFishponds(): Fishpond[] {
  const recentRows = readRecentHighRows();
  return [
    {
      id: "recent-high",
      name: "近期新高池",
      status: "活跃池",
      kind: "技术鱼塘",
      updated: "2026-06-24",
      thesis: "用近期创新高标的做第一层池塘，再用题材新鲜度、筹码干净度、分时强度和板块强度筛掉假突破。",
      events: ["同花顺创新高榜用于快速建池。", "后续增强为 20/60/120 日多周期新高。", "新高只代表市场投票，不代表可以直接追买。"],
      rules: ["优先：题材够新、筹码够干净、分时够强、板块有梯队。", "剔除：爆量长上影、连续加速末端、换手失控但封不住、板块逆势太弱。", "买点：突破后回踩不破，或放量突破后站稳均价线。"],
      rows: recentRows.map((row) => ({
        category: "创新高",
        code: row.code,
        name: row.name,
        status: "观察期",
        logic: `涨跌幅 ${row.pct}%，换手 ${row.turnover}%，前高 ${row.previousHigh}（${row.previousHighDate}）。`,
        trigger: "分时强、题材新、板块有梯队时进入候选。",
        invalidation: "爆量长上影或跌回前高下方。"
      }))
    },
    ...themePonds
  ];
}
