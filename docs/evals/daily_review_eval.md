# Daily Review Evaluation

## Purpose

Evaluate whether a daily review explains the market day, identifies key themes,
and produces review findings that can improve future rules.

## Required Output Fields

- `trade_date`
- `summary`
- `market_regime`
- `findings`
- `data_limits`

## Core Metrics

| Metric | Meaning | Target |
|---|---|---|
| Format compliance | Output can be parsed as structured data | 100% |
| Coverage | Review covers index, breadth, themes, and risks | 80+ |
| Attribution quality | Review explains why the day behaved as it did | 80+ |
| Plan linkage | Review connects to tomorrow plan or watchlist | 80+ |
| Overconfidence control | Uncertain data is marked as uncertain | 90+ |

## Error Types

- `FORMAT_ERROR`
- `MISSING_FIELD`
- `WRONG_REGIME`
- `WRONG_THEME`
- `OVERCONFIDENT`
- `NO_EVIDENCE`

