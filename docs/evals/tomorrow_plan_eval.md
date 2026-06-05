# Tomorrow Plan Evaluation

## Purpose

Evaluate whether a generated tomorrow plan is actionable, evidence-based, and
easy to verify after the next trading day.

## Required Output Fields

- `trade_date`
- `summary`
- `items`
- `data_limits`

Each item should include:

- `theme`
- `priority`
- `action`
- `candidates`
- `confirm_signal`
- `give_up_signal`
- `position_constraint`
- `reasons`

## Core Metrics

| Metric | Meaning | Target |
|---|---|---|
| Format compliance | Output can be parsed as structured data | 100% |
| Field completeness | Required fields are present | 95%+ |
| Actionability | Plan has clear confirm and give-up conditions | 80+ |
| Evidence quality | Conclusions reference market/sector/stock evidence | 80+ |
| Risk control | Position and invalidation constraints are explicit | 80+ |

## Error Types

- `FORMAT_ERROR`
- `MISSING_FIELD`
- `BAD_ACTION`
- `BAD_INVALIDATION`
- `OVERCONFIDENT`
- `NO_EVIDENCE`

## Judge Notes

The judge should not decide whether to trade. It should evaluate whether the
plan is clear, testable, and grounded in evidence.

