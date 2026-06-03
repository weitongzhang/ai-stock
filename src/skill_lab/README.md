# skill_lab

Reusable implementation modules live here. Skill packages in `skills/` should stay thin and call into this layer once modules mature.

Planned domains:

- `market_data`: normalized data providers, symbol mapping, FTShare adapter.
- `stock_selection`: strategy engine, scoring, reports.
- `content_collection`: WeChat article extraction, rendering, comments.
- `shared`: filesystem, CSV, Markdown, logging helpers.
