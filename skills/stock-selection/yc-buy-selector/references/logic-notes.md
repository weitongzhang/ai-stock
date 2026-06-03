# YC-buy Logic Notes

## Corrected Issues

- 2B structure must compute the 20-day moving average on at least 20 valid points. Taking only 10 rows before a 20-day rolling mean makes the downtrend condition always false.
- Breakout checks must compare the latest close with prior resistance/box highs excluding the current bar. Including the current bar makes conditions like `current_close > box_high` impossible when `box_high` includes today's high.
- Major pattern breakout must exclude the current bar from the consolidation range.
- Support/resistance swap should confirm a prior breakthrough before the current retest, not count only the same current bar as the breakthrough.
- Triple-screen long-period data should aggregate OHLCV into period bars (`open=first`, `high=max`, `low=min`, `close=last`, `volume=sum`) instead of sampling every Nth row.
- RSI should handle zero-loss/flat windows without returning unstable NaN/inf values.
- On Windows terminals, configure stdout to UTF-8 before printing checkmarks or Chinese output.

## Signal Hierarchy

1. Highest confidence: three-screen `buy` plus multiple concrete 13-buy-point triggers.
2. Good watchlist: `wait_breakout` plus bottom/retest/pullback buy points.
3. Momentum candidate: `consider_buy` plus breakout buy points 5-8 or multi-timeframe resonance.
4. Low confidence: isolated single signal, sample data only, or no volume confirmation.

## Review Checklist

- Validate required columns: `open`, `high`, `low`, `close`, `volume`.
- Confirm there are enough rows: usually 60+ for most signals, 120+ for major pattern breakout.
- Exclude ST/退市 names when using live A股 lists.
- Keep CSV outputs UTF-8 with BOM (`utf-8-sig`) for Excel compatibility.
