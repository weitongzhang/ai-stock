import { NextResponse } from "next/server";
import type { DailyKPoint, MinutePoint, Quote } from "@/lib/types";

export const dynamic = "force-dynamic";

function normalizeCode(input: string) {
  const match = input.match(/\d{6}/);
  if (!match) return null;
  const code = match[0];
  const isShanghai = code.startsWith("6");
  return {
    code,
    tencent: `${isShanghai ? "sh" : "sz"}${code}`,
    secid: `${isShanghai ? "1" : "0"}.${code}`
  };
}

function toNumber(value: string | undefined): number | null {
  if (value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

async function fetchQuote(symbol: string): Promise<Quote> {
  const response = await fetch(`https://qt.gtimg.cn/q=${symbol}`, { cache: "no-store", signal: AbortSignal.timeout(8000) });
  const buffer = await response.arrayBuffer();
  const text = new TextDecoder("gb18030").decode(buffer);
  const body = text.split("=")[1]?.replace(/^"/, "").replace(/";?$/, "") ?? "";
  const arr = body.split("~");
  const amountWan = toNumber(arr[37]);
  return {
    code: arr[2] ?? "",
    name: arr[1] ?? "",
    price: toNumber(arr[3]),
    preClose: toNumber(arr[4]),
    open: toNumber(arr[5]),
    high: toNumber(arr[33]),
    low: toNumber(arr[34]),
    pct: toNumber(arr[32]),
    amountYi: amountWan === null ? null : amountWan / 10000,
    turnover: toNumber(arr[38]),
    time: arr[30] ?? ""
  };
}

async function fetchMinute(secid: string): Promise<MinutePoint[]> {
  const url = new URL("https://push2his.eastmoney.com/api/qt/stock/trends2/get");
  url.search = new URLSearchParams({
    secid,
    fields1: "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11",
    fields2: "f51,f52,f53,f54,f55,f56,f57,f58",
    iscr: "0",
    iscca: "0",
    ndays: "1"
  }).toString();
  const data = await (await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8000) })).json();
  const trends: string[] = data?.data?.trends ?? [];
  return trends
    .map((item) => {
      const p = item.split(",");
      return { time: p[0], price: Number(p[2]), avg: Number(p[3]), volume: Number(p[5]) };
    })
    .filter((item) => Number.isFinite(item.price));
}

async function fetchDaily(secid: string): Promise<DailyKPoint[]> {
  const url = new URL("https://push2his.eastmoney.com/api/qt/stock/kline/get");
  url.search = new URLSearchParams({
    secid,
    fields1: "f1,f2,f3,f4,f5,f6",
    fields2: "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
    klt: "101",
    fqt: "1",
    beg: "20250101",
    end: "20500101",
    lmt: "90"
  }).toString();
  const data = await (await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8000) })).json();
  const klines: string[] = data?.data?.klines ?? [];
  return klines
    .map((item) => {
      const p = item.split(",");
      return {
        date: p[0],
        open: Number(p[1]),
        close: Number(p[2]),
        high: Number(p[3]),
        low: Number(p[4]),
        volume: Number(p[5])
      };
    })
    .filter((item) => Number.isFinite(item.close));
}

async function fetchDailyFallback(secid: string): Promise<DailyKPoint[]> {
  const url = new URL("https://push2his.eastmoney.com/api/qt/stock/kline/get");
  url.search = new URLSearchParams({
    secid,
    fields1: "f1,f2,f3,f4,f5,f6",
    fields2: "f51,f52,f53,f54,f55,f56",
    klt: "101",
    fqt: "0",
    end: "20500101",
    lmt: "90"
  }).toString();
  const data = await (await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8000) })).json();
  const klines: string[] = data?.data?.klines ?? [];
  return klines
    .map((item) => {
      const p = item.split(",");
      return {
        date: p[0],
        open: Number(p[1]),
        close: Number(p[2]),
        high: Number(p[3]),
        low: Number(p[4]),
        volume: Number(p[5])
      };
    })
    .filter((item) => Number.isFinite(item.close));
}

async function fetchTencentDaily(symbol: string): Promise<DailyKPoint[]> {
  const url = `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${symbol},day,,,90,qfq`;
  const data = await (await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8000) })).json();
  const series: unknown = data?.data?.[symbol]?.day;
  if (!Array.isArray(series)) return [];
  const mapped: Array<DailyKPoint | null> = series
    .map((item) => {
      if (!Array.isArray(item)) return null;
      return {
        date: String(item[0]),
        open: Number(item[1]),
        close: Number(item[2]),
        high: Number(item[3]),
        low: Number(item[4]),
        volume: Number(item[5])
      };
    });
  return mapped.filter((item): item is DailyKPoint => item !== null && Number.isFinite(item.close));
}

export async function GET(_request: Request, context: { params: Promise<{ code: string }> }) {
  const { code } = await context.params;
  const normalized = normalizeCode(code);
  if (!normalized) {
    return NextResponse.json({ error: "无法识别 A 股代码" }, { status: 400 });
  }
  const [quoteResult, minuteResult, dailyResult] = await Promise.allSettled([
    fetchQuote(normalized.tencent),
    fetchMinute(normalized.secid),
    fetchDaily(normalized.secid)
  ]);
  if (quoteResult.status === "rejected") {
    return NextResponse.json({ error: `实时行情获取失败：${quoteResult.reason}` }, { status: 502 });
  }
  const quote = quoteResult.value;
  const minute = minuteResult.status === "fulfilled" ? minuteResult.value : [];
  let daily = dailyResult.status === "fulfilled" ? dailyResult.value : [];
  if (!daily.length) {
    try {
      daily = await fetchDailyFallback(normalized.secid);
    } catch {
      daily = [];
    }
  }
  if (!daily.length) {
    try {
      daily = await fetchTencentDaily(normalized.tencent);
    } catch {
      daily = [];
    }
  }
  return NextResponse.json({ quote, minute, daily });
}
