# market_data

Normalized market data providers and support services.

## Responsibilities

- Fetch or load raw market inputs through provider adapters.
- Normalize different data sources into shared schemas.
- Keep analysis services independent from FTShare, AkShare, Tushare, CSV, or any other source.
- Check data quality before daily planning and review workflows run.
- Provide cache and trading-calendar helpers for repeatable automation.

## Modules

| Module | Purpose |
|---|---|
| `providers.py` | Read-only provider protocol consumed by analysis services |
| `file_provider.py` | Offline provider for examples and smoke tests |
| `ftshare_provider.py` | Adapter skeleton for FTShare skill calls |
| `normalizers.py` | CSV/JSON field normalization into shared schemas |
| `symbols.py` | Market and symbol conversion helpers |
| `cache.py` | JSON cache for provider responses and normalized payloads |
| `quality.py` | Data quality reports, issue taxonomy, and baseline checks |
| `calendar.py` | Weekday fallback calendar and CSV-backed trade calendar |

## Next

- Replace weekday fallback with real exchange holiday calendars.
- Use `JsonCache` inside live providers.
- Add real-data quality baselines after several daily runs.
