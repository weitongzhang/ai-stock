"use client";

import { useEffect, useRef } from "react";
import type { DailyKPoint, MinutePoint } from "@/lib/types";

const MINUTES_PER_DAY = 240;

function minuteIndex(time: string) {
  const clock = time.includes(" ") ? time.split(" ").at(-1) ?? time : time;
  const match = clock.match(/(\d{2}):(\d{2})/);
  if (!match) return null;
  const hour = Number(match[1]);
  const minute = Number(match[2]);
  const total = hour * 60 + minute;
  const morningStart = 9 * 60 + 30;
  const morningEnd = 11 * 60 + 30;
  const afternoonStart = 13 * 60;
  const afternoonEnd = 15 * 60;
  if (total >= morningStart && total <= morningEnd) return total - morningStart;
  if (total >= afternoonStart && total <= afternoonEnd) return 120 + (total - afternoonStart);
  return null;
}

function clear(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function empty(canvas: HTMLCanvasElement, text: string) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  clear(canvas);
  ctx.fillStyle = "#667085";
  ctx.font = "14px Microsoft YaHei, Arial";
  ctx.textAlign = "center";
  ctx.fillText(text, canvas.width / 2, canvas.height / 2);
  ctx.textAlign = "left";
}

function axis(ctx: CanvasRenderingContext2D, min: number, max: number, height: number) {
  ctx.fillStyle = "#667085";
  ctx.font = "12px Arial";
  ctx.fillText(max.toFixed(2), 4, 28);
  ctx.fillText(min.toFixed(2), 4, height - 28);
}

export function MinuteChart({ data, preClose }: { data: MinutePoint[]; preClose?: number | null }) {
  const ref = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    clear(canvas);
    if (!data.length) return empty(canvas, "暂无分时数据");
    const width = canvas.width;
    const height = canvas.height;
    const pad = 28;
    const values = data.map((item) => item.price);
    if (typeof preClose === "number") values.push(preClose);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    ctx.strokeStyle = "#d9dee7";
    ctx.beginPath();
    ctx.moveTo(pad, height - pad);
    ctx.lineTo(width - pad, height - pad);
    ctx.stroke();
    if (typeof preClose === "number") {
      const y = height - pad - ((preClose - min) / span) * (height - pad * 2);
      ctx.strokeStyle = "#cbd5e1";
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(pad, y);
      ctx.lineTo(width - pad, y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.strokeStyle = "#2563eb";
    ctx.lineWidth = 2;
    ctx.beginPath();
    const points = data
      .map((item, fallbackIndex) => ({ item, index: minuteIndex(item.time) ?? fallbackIndex }))
      .filter(({ index }) => index >= 0 && index <= MINUTES_PER_DAY);
    points.forEach(({ item, index }, drawIndex) => {
      const x = pad + (index / MINUTES_PER_DAY) * (width - pad * 2);
      const y = height - pad - ((item.price - min) / span) * (height - pad * 2);
      if (drawIndex === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.fillStyle = "#667085";
    ctx.font = "12px Arial";
    ctx.fillText("09:30", pad, height - 8);
    ctx.fillText("11:30", pad + (120 / MINUTES_PER_DAY) * (width - pad * 2) - 16, height - 8);
    ctx.fillText("15:00", width - pad - 32, height - 8);
    axis(ctx, min, max, height);
  }, [data, preClose]);
  return <canvas ref={ref} width={520} height={280} />;
}

export function DailyKChart({ data }: { data: DailyKPoint[] }) {
  const ref = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    clear(canvas);
    if (!data.length) return empty(canvas, "暂无日K数据");
    const width = canvas.width;
    const height = canvas.height;
    const pad = 28;
    const min = Math.min(...data.map((item) => item.low));
    const max = Math.max(...data.map((item) => item.high));
    const span = max - min || 1;
    const step = (width - pad * 2) / data.length;
    ctx.strokeStyle = "#d9dee7";
    ctx.beginPath();
    ctx.moveTo(pad, height - pad);
    ctx.lineTo(width - pad, height - pad);
    ctx.stroke();
    data.forEach((item, index) => {
      const x = pad + index * step + step / 2;
      const yHigh = height - pad - ((item.high - min) / span) * (height - pad * 2);
      const yLow = height - pad - ((item.low - min) / span) * (height - pad * 2);
      const yOpen = height - pad - ((item.open - min) / span) * (height - pad * 2);
      const yClose = height - pad - ((item.close - min) / span) * (height - pad * 2);
      const up = item.close >= item.open;
      ctx.strokeStyle = up ? "#c2413a" : "#0f8b4c";
      ctx.fillStyle = up ? "#c2413a" : "#0f8b4c";
      ctx.beginPath();
      ctx.moveTo(x, yHigh);
      ctx.lineTo(x, yLow);
      ctx.stroke();
      ctx.fillRect(x - Math.max(step * 0.3, 1), Math.min(yOpen, yClose), Math.max(step * 0.6, 2), Math.max(Math.abs(yClose - yOpen), 1));
    });
    axis(ctx, min, max, height);
  }, [data]);
  return <canvas ref={ref} width={520} height={280} />;
}
