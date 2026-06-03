---
name: sentiment-monitor
description: A股个股舆情与公告风险监控工作流。Use when Codex needs to analyze A-share sentiment, news, announcements, regulatory risks, abnormal movement notices, penalties, lawsuits, shareholder reductions, earnings warnings, major contracts, hot themes, or combine public-opinion signals with technical trading plans, watchlists, or price-action analysis.
---

# Sentiment Monitor

Use this skill to add a public-opinion and event-risk layer to A-share analysis.

## Workflow

1. Identify the stock code and name. Use `600000.SH` / `000001.SZ` style when calling FTShare and `600000.XSHG` / `000001.SZ` style for K-line calls if needed.
2. Run the script for a first-pass sentiment check:

```powershell
python skills\sentiment\sentiment-monitor\scripts\sentiment_check.py --symbol 600481.SH --name 双良节能 --out-dir examples\market\sentiment
```

3. Read the Markdown report and combine it with technical structure:
   - Negative hard events lower the weight of technical buy signals.
   - Abnormal-movement notices make breakout trades require stronger follow-through.
   - Positive themes without price confirmation are watchlist items, not direct entries.
   - Strong price action against negative news requires explicit risk controls.
4. If the user asks for a watchlist update, copy the risk tags and next-check trigger into `watchlist-tracker`.

## Report Interpretation

- `red`: hard negative risk, such as regulatory investigation, punishment, fraud, delisting, major lawsuit, debt/default, large loss, or forced liquidation. Avoid treating technical rebounds as normal pullbacks.
- `orange`: material uncertainty, such as abnormal movement notice, inquiry letter, earnings warning, large reduction, pledge, or rumor clarification. Require confirmation and smaller risk.
- `green`: constructive event, such as major order, buyback, performance growth, product launch, policy support, or industry demand.
- `neutral`: no strong directional event found in the scanned text.

## References

Read `references/risk-taxonomy.md` when changing risk labels, adding keywords, or deciding how sentiment should modify technical action.

