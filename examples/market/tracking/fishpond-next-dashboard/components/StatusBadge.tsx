import type { PondStatus, StockStatus } from "@/lib/types";

const styles: Record<string, string> = {
  富矿池: "bg-emerald-50 text-emerald-700",
  活跃池: "bg-blue-50 text-blue-700",
  观察池: "bg-amber-50 text-amber-700",
  贫瘠池: "bg-red-50 text-red-700",
  保留: "bg-emerald-50 text-emerald-700",
  观察期: "bg-violet-50 text-violet-700",
  待核实: "bg-slate-100 text-slate-700",
  降级: "bg-orange-50 text-orange-700",
  剔除: "bg-red-50 text-red-700"
};

export function StatusBadge({ status }: { status: PondStatus | StockStatus | string }) {
  return (
    <span className={`status-pill inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold ${styles[status] ?? "bg-blue-50 text-blue-700"}`}>
      {status}
    </span>
  );
}
