# 2026-06-04 A股市场宽度快照

> 研究用途，非投资建议。

## 核心指标

- 两市成交额：-
- 涨跌家数：上涨 - / 下跌 - / 平盘 -
- 涨跌停：涨停 80 / 炸板 19 / 跌停 7
- 情绪质量：封板率 80.81%，炸板率 19.19%
- 连板结构：连板 10，最高连板 4

## 明细

| 指标 | 数值 | 来源 | 备注 |
|---|---:|---|---|
| 涨停数 | 80 | eastmoney:stock_zt_pool_em |  |
| 连板家数 | 10 | eastmoney:stock_zt_pool_em |  |
| 最高连板 | 4 | eastmoney:stock_zt_pool_em |  |
| 涨停封板资金 | 81.13 | eastmoney:stock_zt_pool_em | 亿元 |
| 炸板数 | 19 | eastmoney:stock_zt_pool_zbgc_em |  |
| 跌停数 | 7 | eastmoney:stock_zt_pool_dtgc_em |  |
| 炸板率 | 19.19 | derived:eastmoney_limit_pools | % |
| 封板率 | 80.81 | derived:eastmoney_limit_pools | % |

## 采集限制

- stock_zh_a_spot_em: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
- stock_market_fund_flow: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
