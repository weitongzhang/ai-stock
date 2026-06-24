export type PondStatus = "富矿池" | "活跃池" | "观察池" | "贫瘠池";
export type StockStatus = "保留" | "观察期" | "降级" | "剔除" | "待核实";

export interface FishpondRow {
  category: string;
  code: string;
  name: string;
  status: StockStatus | string;
  logic: string;
  trigger: string;
  invalidation: string;
}

export interface MarketLinks {
  eastmoney?: string;
  ths?: string;
}

export interface RecentHighRow {
  code: string;
  name: string;
  pct: string;
  turnover: string;
  price: string;
  previousHigh: string;
  previousHighDate: string;
}

export interface Fishpond {
  id: string;
  name: string;
  status: PondStatus;
  kind: string;
  updated: string;
  thesis: string;
  events: string[];
  rules: string[];
  rows: FishpondRow[];
}

export interface Quote {
  code: string;
  name: string;
  price: number | null;
  preClose: number | null;
  open: number | null;
  high: number | null;
  low: number | null;
  pct: number | null;
  amountYi: number | null;
  turnover: number | null;
  time: string;
}

export interface MinutePoint {
  time: string;
  price: number;
  avg?: number;
  volume?: number;
}

export interface DailyKPoint {
  date: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume?: number;
}
