# 2026-06-05 A股市场宽度快照

> 研究用途，非投资建议。

## 结论：盘前/待确认

今天盘面宽度尚未形成，先参考最近已完成交易日背景；等9:35-10:00后重新采集，再决定是否提高进攻性。

依据：
- 今日涨跌停池仍为空，当前不作为真实盘面宽度判断
- 近几日背景已保留，可用于盘前制定观察计划
- 最近已完成交易日炸板率低于前期均值，封板质量改善
- 最近已完成交易日跌停数低于前期均值，亏钱效应收敛
- 成交额和涨跌家数缺失，仓位结论需要保守使用

## 核心指标

- 两市成交额：暂无
- 涨跌家数：上涨 暂无 / 下跌 暂无 / 平盘 暂无
- 涨跌停：涨停 0 / 炸板 0 / 跌停 0
- 情绪质量：封板率 0.0%，炸板率 0.0%
- 连板结构：连板 暂无，最高连板 暂无

## 近几日背景

| 日期 | 涨停 | 炸板 | 跌停 | 封板率 | 炸板率 | 连板家数 | 最高连板 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-29 | 49 | 38 | 50 | 56.32 | 43.68 | 9 | 5 |
| 2026-06-01 | 120 | 41 | 21 | 74.53 | 25.47 | 11 | 4 |
| 2026-06-02 | 67 | 21 | 16 | 76.14 | 23.86 | 16 | 3 |
| 2026-06-03 | 66 | 51 | 11 | 56.41 | 43.59 | 11 | 3 |
| 2026-06-04 | 80 | 19 | 7 | 80.81 | 19.19 | 10 | 4 |

- 涨停趋势差：4.5，炸板率趋势差：-14.96%，跌停趋势差：-17.5

## 明细

| 指标 | 数值 | 来源 | 备注 |
|---|---:|---|---|
| 涨停数 | 0 | eastmoney:stock_zt_pool_em |  |
| 炸板数 | 0 | eastmoney:stock_zt_pool_zbgc_em |  |
| 跌停数 | 0 | eastmoney:stock_zt_pool_dtgc_em |  |
| 炸板率 | 0.0 | derived:eastmoney_limit_pools | % |
| 封板率 | 0.0 | derived:eastmoney_limit_pools | % |
| 今日涨跌停数据状态 | 未更新 | derived:current_limit_pools | 盘前或数据源未更新 |
| 近N日样本数 | 5 | derived:market_breadth_history |  |
| 近几日涨停均值 | 75.5 | derived:market_breadth_history |  |
| 近几日炸板率均值 | 34.15 | derived:market_breadth_history | % |
| 近几日跌停均值 | 24.5 | derived:market_breadth_history |  |
| 近几日最高连板均值 | 3.75 | derived:market_breadth_history |  |
| 涨停趋势差 | 4.5 | derived:market_breadth_history |  |
| 炸板率趋势差 | -14.96 | derived:market_breadth_history | % |
| 跌停趋势差 | -17.5 | derived:market_breadth_history |  |
| 连板高度趋势差 | 0.25 | derived:market_breadth_history |  |
