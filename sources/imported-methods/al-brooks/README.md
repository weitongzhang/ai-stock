# Al Brooks Price Action Methodology

来源背景：根据 Al Brooks 价格行为交易体系的公开概念和常见术语整理，重点提炼为可训练、可执行、可复盘的方法论。本文件不是原书摘录，也不是逐字稿。

研究状态：外部方法论沉淀。规则未经系统回测和样本验证前，先保存在 `sources/imported-methods/`；后续验证成熟后，再转化为明确的观察池、交易复盘、图例库或 skill 逻辑。

风险说明：本文仅用于技术分析研究，不构成投资建议。

## 核心主线

Brooks 方法论的主线不是“看到某个形态就交易”，而是：

```text
市场状态 -> 买卖压力 -> 结构位置 -> 信号质量 -> 风险计划 -> 后续跟随
```

最重要的一句话：

```text
同一个价格形态，在不同市场状态下意义完全不同。
```

## 文件说明

- `docs/AL_BROOKS_PRICE_ACTION_METHODOLOGY.md`：完整方法论总纲。
- `sources/imported-methods/al-brooks/playbook.md`：日常执行剧本、评分表和复盘模板。

## 后续沉淀方向

1. 建立 A股日线案例库。
2. 建立分钟线训练样本。
3. 把 H1/H2、L1/L2、突破回调、失败突破、主要趋势反转分别整理成图例。
4. 与现有 YC-buy 技术选股结果结合，用 Brooks 结构做二次确认。
5. 形成可由 Codex 调用的交易复盘 skill。

## 与 BSA 框架的关系

Brooks 方法论在 BSA 价格行为框架中主要承担“结构”和“行动”两层：

```text
BSA = Background + Structure + Action
方方土方法论 -> Background / 急迫感 / 反馈
Al Brooks 方法论 -> Structure / 信号计数 / 执行
```

统一融合稿见：`sources/imported-methods/bsa-price-action-framework.md`。
