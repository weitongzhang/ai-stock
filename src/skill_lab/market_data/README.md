# market_data

Future home for normalized market data providers.

Initial target:

- Wrap `skills/market-data/ftshare-market-data/run.py` and subskill handlers.
- Normalize A 股 symbols to `000001.SZ`, `600000.XSHG`, `920036.BJ` as needed.
- Return OHLCV data as pandas DataFrames for strategy consumers.
