"use client";

import { useMemo, useState } from "react";
import type { Fishpond, FishpondRow } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";
import { StockModal } from "./StockModal";

export function DashboardClient({ ponds }: { ponds: Fishpond[] }) {
  const [selectedId, setSelectedId] = useState(ponds[0]?.id ?? "");
  const [pondSearch, setPondSearch] = useState("");
  const [status, setStatus] = useState("全部");
  const [tableSearch, setTableSearch] = useState("");
  const [selectedRow, setSelectedRow] = useState<FishpondRow | null>(null);

  const filteredPonds = useMemo(() => {
    return ponds.filter((pond) => {
      const statusOk = status === "全部" || pond.status === status;
      const q = pondSearch.trim().toLowerCase();
      const textOk = !q || JSON.stringify(pond).toLowerCase().includes(q);
      return statusOk && textOk;
    });
  }, [pondSearch, ponds, status]);

  const selected = ponds.find((pond) => pond.id === selectedId) ?? filteredPonds[0] ?? ponds[0];
  const rows = useMemo(() => {
    const q = tableSearch.trim().toLowerCase();
    return selected.rows.filter((row) => !q || JSON.stringify(row).toLowerCase().includes(q));
  }, [selected, tableSearch]);

  return (
    <>
      <header className="border-b-4 border-[#d33f2f] bg-slate-950 text-white">
        <div className="mx-auto max-w-[1500px] px-4 py-5">
          <h1 className="text-2xl font-extrabold tracking-normal">统一鱼塘看板</h1>
          <p className="mt-2 text-sm text-slate-300">近期新高池和主题鱼塘统一跟踪。先看鱼塘质量，再看标的、触发、失效和观察状态。</p>
        </div>
      </header>
      <main className="mx-auto grid max-w-[1500px] grid-cols-1 gap-4 p-4 lg:grid-cols-[310px_minmax(0,1fr)]">
        <aside className="min-w-0 self-start rounded-lg border border-line bg-white p-3 shadow lg:sticky lg:top-3">
          <div className="grid gap-2">
            <input className="rounded-md border border-line px-3 py-2 text-sm" value={pondSearch} onChange={(event) => setPondSearch(event.target.value)} placeholder="搜索鱼塘/标的/代码" />
            <select className="rounded-md border border-line px-3 py-2 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {["全部", "富矿池", "活跃池", "观察池", "贫瘠池"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
          <div className="mt-3 grid gap-2">
            {filteredPonds.map((pond) => (
              <button key={pond.id} className={`rounded-md border p-3 text-left ${pond.id === selected.id ? "border-blue-500 bg-blue-50" : "border-line bg-white"}`} onClick={() => { setSelectedId(pond.id); setTableSearch(""); }}>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold">{pond.name}</span>
                  <StatusBadge status={pond.status} />
                </div>
                <div className="mt-1 text-xs text-muted">{pond.kind} · {pond.rows.length} 个标的</div>
              </button>
            ))}
          </div>
        </aside>

        <div className="grid min-w-0 gap-4">
          <section className="min-w-0 rounded-lg border border-line bg-white p-4 shadow">
            <div className="grid items-start gap-3 md:grid-cols-[minmax(0,1fr)_auto]">
              <div className="min-w-0">
                <h2 className="text-xl font-extrabold">{selected.name}</h2>
                <p className="mt-2 leading-6 text-muted">{selected.thesis}</p>
              </div>
              <div className="flex w-fit max-w-full flex-wrap items-center justify-end gap-2 justify-self-start rounded-lg bg-transparent p-0 md:justify-self-end">
                <StatusBadge status={selected.status} />
                <span className="inline-flex min-h-6 items-center justify-center whitespace-nowrap rounded-full bg-blue-50 px-2.5 py-1 text-xs font-bold leading-none text-blue-700">{selected.kind}</span>
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-4">
              {[["鱼塘质量", selected.status], ["鱼塘类型", selected.kind], ["跟踪标的", selected.rows.length], ["更新时间", selected.updated]].map(([label, value]) => (
                <div key={label} className="rounded-lg bg-slate-100 p-3">
                  <div className="text-lg font-extrabold">{value}</div>
                  <div className="mt-1 text-xs text-muted">{label}</div>
                </div>
              ))}
            </div>
          </section>

          <div className="grid gap-4 xl:grid-cols-2">
            <section className="rounded-lg border border-line bg-white p-4 shadow">
              <h3 className="mb-2 font-bold">核心事件</h3>
              <ul className="list-disc space-y-1 pl-5 leading-6 text-slate-700">{selected.events.map((item) => <li key={item}>{item}</li>)}</ul>
            </section>
            <section className="rounded-lg border border-line bg-white p-4 shadow">
              <h3 className="mb-2 font-bold">触发与失效</h3>
              <ul className="list-disc space-y-1 pl-5 leading-6 text-slate-700">{selected.rules.map((item) => <li key={item}>{item}</li>)}</ul>
            </section>
          </div>

          <section className="min-w-0 rounded-lg border border-line bg-white p-4 shadow">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <h3 className="mr-auto font-bold">标的列表</h3>
              <input className="rounded-md border border-line px-3 py-2 text-sm" value={tableSearch} onChange={(event) => setTableSearch(event.target.value)} placeholder="搜索表格" />
            </div>
            <div className="max-w-full overflow-auto rounded-lg border border-line">
              <table className="stock-table min-w-[1180px] w-full border-collapse text-sm">
                <thead className="bg-slate-50 text-left text-slate-700">
                  <tr>
                    {[
                      ["分类", "col-category"],
                      ["代码", "col-code"],
                      ["名称", "col-name"],
                      ["外链", "col-status"],
                      ["状态", "col-status"],
                      ["逻辑", "col-logic"],
                      ["触发", ""],
                      ["失效", ""]
                    ].map(([header, klass]) => <th key={header} className={`border-b border-line px-3 py-2 ${klass}`}>{header}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={`${row.code}-${row.name}-${row.category}`} className="cursor-pointer hover:bg-blue-50/50" onClick={() => setSelectedRow(row)}>
                      <td className="border-b border-line px-3 py-2">{row.category}</td>
                      <td className="border-b border-line px-3 py-2 font-mono text-slate-600">{row.code}</td>
                      <td className="border-b border-line px-3 py-2 font-bold">{row.name}</td>
                      <td className="border-b border-line px-3 py-2" onClick={(event) => event.stopPropagation()}>
                        {/\d{6}/.test(row.code) ? (
                          <div className="flex flex-wrap gap-1">
                            <a className="rounded bg-red-50 px-2 py-1 text-xs font-bold text-red-700 hover:bg-red-100" href={`https://quote.eastmoney.com/${row.code.startsWith("6") ? "sh" : "sz"}${row.code.match(/\d{6}/)?.[0]}.html`} target="_blank" rel="noreferrer">东财</a>
                            <a className="rounded bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700 hover:bg-blue-100" href={`https://stockpage.10jqka.com.cn/${row.code.match(/\d{6}/)?.[0]}/`} target="_blank" rel="noreferrer">同花顺</a>
                          </div>
                        ) : "-"}
                      </td>
                      <td className="border-b border-line px-3 py-2"><StatusBadge status={row.status} /></td>
                      <td className="border-b border-line px-3 py-2">{row.logic}</td>
                      <td className="border-b border-line px-3 py-2">{row.trigger}</td>
                      <td className="border-b border-line px-3 py-2">{row.invalidation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>
      <StockModal row={selectedRow} onClose={() => setSelectedRow(null)} />
    </>
  );
}
