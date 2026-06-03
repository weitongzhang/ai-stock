# Sentiment Monitoring

This module is the future implementation layer for A-share sentiment and event-risk monitoring.

Current first-pass capability lives in:

```text
skills/sentiment/sentiment-monitor/
```

## Intended Inputs

- Stock code and name
- FTShare `stock-security-info`
- FTShare `semantic-search-news`
- Future: announcements, research reports, exchange letters, interactive platform, social trend data

## Intended Outputs

- Risk labels: `red`, `orange`, `green`, `neutral`
- Evidence snippets and source links
- Technical-trading impact notes
- Watchlist trigger/invalidation updates

## Integration Rule

Sentiment does not replace price action. It changes the risk budget and signal weight:

```text
sentiment/event risk -> risk color
price action -> market confirmation
volume -> urgency
follow-through -> validity
watchlist -> next check
```

