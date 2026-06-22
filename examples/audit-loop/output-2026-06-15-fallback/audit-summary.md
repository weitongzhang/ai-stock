# Minimal Auditable Research Loop

- Run ID: `daily:2026-06-15`
- Plan ID: `plan:2026-06-15`
- State: `EVALUATED_WITH_GAPS`
- Closure coverage: `40.0%`
- Evaluation score: `70.0`

## Journal

- `plan_created`
- `plan_outcome`
- `plan_evaluated`

## Plan Items

### plan:2026-06-15:item:1 - 能源/煤炭/油气

- Action: `core_dip`
- Confirmation: 能源/煤炭/油气前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。
- Invalidation: 能源/煤炭/油气核心低开低走、冲高回落，或消息强但板块无量无扩散。
- Closure: `triggered`

### plan:2026-06-15:item:2 - AI算力/数据中心

- Action: `core_dip`
- Confirmation: AI算力/数据中心前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。
- Invalidation: AI算力/数据中心核心低开低走、冲高回落，或消息强但板块无量无扩散。
- Closure: `unresolved`

### plan:2026-06-15:item:3 - 6G/通信/卫星互联网

- Action: `watch`
- Confirmation: 6G/通信/卫星互联网前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。
- Invalidation: 6G/通信/卫星互联网核心低开低走、冲高回落，或消息强但板块无量无扩散。
- Closure: `unresolved`

### plan:2026-06-15:item:4 - 半导体/国产替代

- Action: `watch`
- Confirmation: 半导体/国产替代前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。
- Invalidation: 半导体/国产替代核心低开低走、冲高回落，或消息强但板块无量无扩散。
- Closure: `unresolved`

### plan:2026-06-15:item:5 - 消费/旅游/短剧

- Action: `give_up`
- Confirmation: 消费/旅游/短剧前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。
- Invalidation: 消费/旅游/短剧核心低开低走、冲高回落，或消息强但板块无量无扩散。
- Closure: `invalidated`

## Interpretation

This example intentionally leaves some plan items unresolved. The audit score exposes the gap instead of silently treating the workflow as complete.
