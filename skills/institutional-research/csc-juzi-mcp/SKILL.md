---
name: csc-juzi-mcp
description: |
  Use this skill when the user asks to use the CSCI Juzi / 中信建投 Juzi MCP services for fund research,
  fund manager research, asset allocation, industry scoring, quant strategy context, backtest context,
  strategy cards, or institutional research evidence. This skill routes MCP outputs into the trading
  research workspace without storing credentials.
---

# CSCI Juzi MCP Integration

Use this skill to bring CSCI Juzi MCP outputs into the trading research system as
external institutional evidence.

## Safety Boundary

Never write MCP tokens, live authentication headers, access-token strings, or
full live MCP client configs into this repository. Credentials stay only in the
local MCP client configuration.

If the user provides MCP output, treat it as external evidence. Preserve the
source server, topic, evidence date, summary, supports, cautions, conflicts,
follow-up checks and confidence.

## Server Routing

| Server | Use For | Workspace Role |
|---|---|---|
| `juzi-fund` | fund characteristics, holdings, returns, risk, attribution, crowding | fund research evidence |
| `juzi-manager` | fund manager notes and interview knowledge | manager research evidence |
| `juzi-stratos` | industry score, macro state, asset allocation, quant strategy, backtest context | allocation and strategy evidence |
| `juzi-skills` | workflow guides and code templates | development support only |
| `juzi-report` | quant strategy cards | reporting and Harness evidence |

## Workflow

1. Run the local market/sector/stock pipeline first.
2. Use Juzi MCP to collect external institutional evidence.
3. Normalize the evidence with `src/skill_lab/institutional_research/context.py`.
4. Attach the result as `raw["institutional_context"]` in plans, reviews or Harness samples.
5. Record conflicts explicitly; do not let institutional evidence overwrite local data conclusions.

## Conflict Handling

- If Juzi allocation conflicts with market regime, keep both and require a validation trigger.
- If Juzi industry score conflicts with local theme strength, treat it as counterevidence.
- If fund/manager thesis conflicts with short-term execution, separate thesis from timing.
- If evidence has no date or source, mark it as a data limit and lower confidence.
