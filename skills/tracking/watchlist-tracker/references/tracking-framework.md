# Tracking Framework

## Horizons

| Horizon | Typical Cadence | Focus |
|---|---|---|
| `long` | weekly/monthly | thesis, industry cycle, valuation, major trend, fundamental catalyst |
| `mid` | daily/weekly | trend stage, sector rotation, key support/resistance, volume structure |
| `short` | intraday/daily | trigger, breakout/retest, stop/invalidation, 1-5 day execution |

## Item Types

- `stock`: individual A-share/HK/US stock.
- `sector`: industry or board-level sector.
- `theme`: narrative/theme such as AI, robotics, low-altitude economy.
- `etf`: tradable ETF proxy.
- `index`: broad or thematic index.

## Status Values

- `watching`: on watch, no trigger yet.
- `triggered`: condition fired, needs review.
- `active`: currently being tracked as active candidate.
- `cooldown`: wait after failed breakout or overheat.
- `invalidated`: thesis or technical setup failed.
- `archived`: no longer tracked.

## Required Fields

- `symbol`
- `name`
- `item_type`
- `horizon`
- `status`
- `thesis`
- `key_levels`
- `trigger`
- `invalidation`
- `next_check`
- `notes`

## Report Sections

1. Triggered today
2. Short-term action watch
3. Mid-term structure changes
4. Long-term thesis updates
5. Invalidated or cooldown items
