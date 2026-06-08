# Blogger Perspective Skill Integration

This note records how the two distilled Douyin perspective packages are wired
into the trading research workspace.

| Skill | Domain | Role | Best Used For | Coordinates With |
|---|---|---|---|---|
| `chen-xiaoqun-perspective` | `stock-selection` | Short-term theme, leader and emotion-cycle perspective | Mainline theme review, leader candidate checks, turnover/acceptance, chart-cycle observation, next-day validation boundaries | `a-share-market-flow-analyst`, `watchlist-tracker` |
| `model-xiansheng-perspective` | `methodology` | Dialectical finance and principal-contradiction perspective | Qualitative-change thesis, main contradiction, market-stage reasoning, risk and execution discipline, methodology reflection | `ftshare-market-data`, `a-share-market-flow-analyst`, `qiushi-stock-analysis`, `watchlist-tracker` |

## Integration Policy

The zip packages are treated as perspective skills, not as market data sources.
They can structure judgment, generate checklists and provide analysis language,
but current facts must still come from the data provider, market-flow reports,
index environment, breadth snapshots, K-line data, news feeds or user-supplied
materials.

The integrated copy keeps the executable skill surface and curated knowledge
base:

| Kept | Reason |
|---|---|
| `SKILL.md` | Activation rules, safety boundary and workflow |
| `agents/openai.yaml` | Future agent routing entry |
| `scripts/` | Local search, validation and quality-check tools |
| `references/knowledge/` | High-fidelity distilled knowledge catalog |
| `references/research/` | Distillation notes and validation context |
| top-level audit reports | Coverage and preservation trace |

Raw `references/sources/` media and source dumps were intentionally not copied
into the repository during this integration pass. The original zip files remain
the raw archive. This keeps the repository usable and avoids committing large
media assets or unstable exported filenames.

## Harness Usage

In the Harness, these skills should become judge and reasoning dimensions rather
than standalone predictors:

| Harness Stage | Chen Xiaoqun Perspective | Model Xiansheng Perspective |
|---|---|---|
| Daily review | Was the actual market mainline identified? Did leader behavior confirm or reject the theme? | What was the principal market contradiction today? Did the review distinguish facts, expectation and execution? |
| Tomorrow plan | Which themes deserve observation, and what would confirm leadership? | Which thesis is still alive, what would falsify it, and what risk should cap action? |
| Sector analysis | Theme duration, leader role, turnover acceptance, emotion stage | Sector contradiction, policy/industry/market structure, stage of expectation |
| Stock analysis | Candidate role, chart-cycle score, acceptance and exit condition | Qualitative-change evidence, valuation expectation, contradiction and counterevidence |
| Retrospective eval | Whether theme/leader assumptions were validated | Whether the original contradiction framing was useful after outcomes appeared |

## Agent Boundary

Each perspective can later receive a specialized agent, but the first production
step should be orchestration through the existing Harness:

| Agent | Needed Now | Future Entry |
|---|---|---|
| `ChenXiaoqunPerspectiveAgent` | Optional | Add when daily theme and leader reviews require repeated templated outputs |
| `ModelXianshengPerspectiveAgent` | Optional | Add when methodology reflection, thesis review and risk framing need separate evals |

Until then, the domains should call the skills as tools:

1. Data layer supplies latest facts.
2. Market-flow and sector modules summarize observable structure.
3. Perspective skills transform facts into checklists, contradiction framing and
   validation boundaries.
4. Harness judges whether the framing improved review and planning quality.
