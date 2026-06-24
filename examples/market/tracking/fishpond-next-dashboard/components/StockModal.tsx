"use client";

import { useEffect, useMemo, useState } from "react";
import type { DailyKPoint, FishpondRow, MinutePoint, Quote } from "@/lib/types";
import { DailyKChart, MinuteChart } from "./StockChart";

interface StockPayload {
  quote: Quote;
  minute: MinutePoint[];
  daily: DailyKPoint[];
}

function normalizeCode(code: string) {
  const match = code.match(/\d{6}/);
  return match?.[0] ?? null;
}

function marketPrefix(code: string) {
  return code.startsWith("6") ? "1" : "0";
}

function eastmoneyUrl(code: string) {
  return `https://quote.eastmoney.com/${code.startsWith("6") ? "sh" : "sz"}${code}.html`;
}

function thsUrl(code: string) {
  return `https://stockpage.10jqka.com.cn/${code}/`;
}

function isMarketOpen() {
  const now = new Date();
  const day = now.getDay();
  if (day === 0 || day === 6) return false;
  const minutes = now.getHours() * 60 + now.getMinutes();
  return (minutes >= 9 * 60 + 25 && minutes <= 11 * 60 + 30) || (minutes >= 13 * 60 && minutes <= 15 * 60 + 5);
}

export function StockModal({ row, onClose }: { row: FishpondRow | null; onClose: () => void }) {
  const [payload, setPayload] = useState<StockPayload | null>(null);
  const [error, setError] = useState("");
  const [lastRefresh, setLastRefresh] = useState("");
  const code = useMemo(() => (row ? normalizeCode(row.code) : null), [row]);

  useEffect(() => {
    if (!row || !code) return;
    let active = true;
    let timer: ReturnType<typeof setInterval> | null = null;
    async function load() {
      try {
        setError("");
        const data = (await (await fetch(`/api/stock/${code}`, { cache: "no-store" })).json()) as StockPayload & { error?: string };
        if (!active) return;
        if ("error" in data && data.error) throw new Error(data.error);
        setPayload(data);
        setLastRefresh(new Date().toLocaleTimeString("zh-CN", { hour12: false }));
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : String(err));
      }
    }
    setPayload(null);
    void load();
    timer = setInterval(load, isMarketOpen() ? 15_000 : 60_000);
    return () => {
      active = false;
      if (timer) clearInterval(timer);
    };
  }, [row, code]);

  if (!row) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 p-4" onClick={onClose}>
      <div className="max-h-[92vh] w-full max-w-[1180px] overflow-auto rounded-lg border border-line bg-white shadow-2xl" onClick={(event) => event.stopPropagation()}>
        <div className="flex items-start justify-between gap-4 border-b border-line p-4">
          <div>
            <div className="text-xl font-extrabold">{payload?.quote.name || row.name} {code || row.code}</div>
            <div className="mt-1 text-sm text-muted">
              {code ? `行情时间：${payload?.quote.time || "-"} · 最新刷新：${lastRefresh || "-"}` : "该行不是可识别的 A 股代码，暂不支持图表。"}
            </div>
            {code ? (
              <div className="mt-3 flex flex-wrap gap-2">
                <a className="rounded-md bg-red-50 px-3 py-2 text-sm font-bold text-red-700 hover:bg-red-100" href={eastmoneyUrl(code)} target="_blank" rel="noreferrer">
                  东方财富行情
                </a>
                <a className="rounded-md bg-blue-50 px-3 py-2 text-sm font-bold text-blue-700 hover:bg-blue-100" href={thsUrl(code)} target="_blank" rel="noreferrer">
                  同花顺行情
                </a>
                <a className="rounded-md bg-slate-100 px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-200" href={`https://quote.eastmoney.com/concept/${marketPrefix(code)}.${code}.html`} target="_blank" rel="noreferrer">
                  东方财富详情
                </a>
              </div>
            ) : null}
          </div>
          <button className="rounded-md border border-line px-3 py-2 text-sm" onClick={onClose}>关闭</button>
        </div>

        {!code ? (
          <div className="p-5 text-muted">可识别格式包括 000001、600000、000001.XSHE、600000.XSHG 等。</div>
        ) : error ? (
          <div className="p-5 text-red-700">行情接口加载失败：{error}</div>
        ) : !payload ? (
          <div className="p-5 text-muted">正在加载行情图表...</div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-3 p-4 md:grid-cols-4 xl:grid-cols-6">
              {[
                ["现价", payload.quote.price ?? "-"],
                ["涨跌幅", payload.quote.pct === null ? "-" : `${payload.quote.pct}%`],
                ["今开", payload.quote.open ?? "-"],
                ["最高", payload.quote.high ?? "-"],
                ["最低", payload.quote.low ?? "-"],
                ["昨收", payload.quote.preClose ?? "-"],
                ["成交额", payload.quote.amountYi === null ? "-" : `${payload.quote.amountYi.toFixed(2)} 亿`],
                ["换手", payload.quote.turnover === null ? "-" : `${payload.quote.turnover}%`]
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg bg-slate-100 p-3">
                  <div className="text-lg font-extrabold">{value}</div>
                  <div className="mt-1 text-xs text-muted">{label}</div>
                </div>
              ))}
            </div>
            <div className="grid gap-4 px-4 pb-4 xl:grid-cols-2">
              <div className="min-w-0 rounded-lg border border-line p-3">
                <h3 className="mb-2 font-bold">分时概览</h3>
                <MinuteChart data={payload.minute} preClose={payload.quote.preClose} />
              </div>
              <div className="min-w-0 rounded-lg border border-line p-3">
                <h3 className="mb-2 font-bold">日K走势</h3>
                <DailyKChart data={payload.daily.length ? payload.daily : minuteAsDaily(payload.minute, payload.quote)} />
              </div>
            </div>
            <div className="px-4 pb-4 text-sm leading-6 text-muted">
              弹窗打开期间自动刷新。交易时间约 15 秒刷新一次，非交易时间约 60 秒刷新一次。
              {!payload.daily.length ? " 日K历史接口暂未返回数据，右侧先用当日分时合成单根K线占位，避免空白误判。" : ""}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function minuteAsDaily(minute: MinutePoint[], quote: Quote): DailyKPoint[] {
  if (!minute.length) return [];
  const prices = minute.map((item) => item.price).filter(Number.isFinite);
  if (!prices.length) return [];
  return [{
    date: quote.time?.slice(0, 8) || new Date().toISOString().slice(0, 10),
    open: quote.open ?? prices[0],
    close: quote.price ?? prices[prices.length - 1],
    high: quote.high ?? Math.max(...prices),
    low: quote.low ?? Math.min(...prices),
    volume: undefined
  }];
}
