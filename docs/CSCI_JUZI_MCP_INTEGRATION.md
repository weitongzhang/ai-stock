# CSCI Juzi MCP Integration

This note defines how to integrate the CSCI Juzi MCP services into the trading
research workspace without committing credentials.

## Security Boundary

Never commit MCP credentials to this repository.

Do not add any file containing:

| Secret Shape | Example Pattern |
|---|---|
| Live auth header | a real HTTP authentication header value |
| Juzi access token | any live Juzi-issued access token string |
| Full MCP client config | live server config with credential headers |

Live MCP configuration belongs only in the local MCP client configuration used
by Codex, Claude Code, Cursor, Qoder, or another client. The repository may
document server names and integration boundaries, but not secrets.

## Architecture Placement

The CSCI Juzi MCP services are an external institutional research layer, not the
primary market data layer.

| MCP Server | Workspace Role | Primary Consumer |
|---|---|---|
| `juzi-fund` | Fund characteristics, holdings, returns, risk, attribution, crowding | `institutional-research` |
| `juzi-manager` | Fund manager research notes and interview knowledge | `institutional-research` |
| `juzi-stratos` | Industry scoring, macro state, asset allocation, quant strategy and backtest context | `institutional-research`, `backtesting` |
| `juzi-skills` | Skill registry, workflow guide and code templates | developer workflow only |
| `juzi-report` | Quant strategy cards | reporting and Harness evidence |

## Data Flow

```text
Local MCP client
  -> Juzi MCP servers
  -> manually or tool-collected MCP outputs
  -> InstitutionalResearchContext
  -> planning raw["institutional_context"]
  -> Harness / daily review / tomorrow plan
```

The MCP layer should enrich judgment with institutional evidence. It must not
overwrite FTShare data, market breadth, sector strength, leader extraction,
methodology conflicts, or backtest metrics.

## Conflict Policy

| Conflict | Handling |
|---|---|
| Juzi asset allocation conflicts with market regime | Keep both views; mark conflict and require validation trigger |
| Juzi industry score conflicts with local theme strength | Treat as external counterevidence, not replacement |
| Fund/manager view conflicts with short-term trading signal | Separate long-term allocation thesis from short-term execution |
| MCP output lacks date/source | Add data limit and lower confidence |

## Engineering Entry

| File | Purpose |
|---|---|
| `skills/institutional-research/csc-juzi-mcp/SKILL.md` | Runtime-facing routing skill |
| `src/skill_lab/institutional_research/schemas.py` | Structured institutional research records |
| `src/skill_lab/institutional_research/context.py` | Convert MCP-derived records into planning context |
| `tests/smoke/test_institutional_research_context.py` | Validate schema, conflict handling and secret hygiene |

## Recommended Operating Rule

Use Juzi MCP after the local market/sector pipeline has produced its own
conclusion. Ask the MCP layer for institutional confirmation, counterevidence,
fund positioning, manager perspective, allocation state or strategy-card
context. Then record differences explicitly.
