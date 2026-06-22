# Research Agent

This package is the deterministic runtime for the first A-share research agent.
It coordinates tested domain services without allowing autonomous trading.

Supported tasks:

- `post-market-review`: classify the market and themes, then build a review and tomorrow plan.
- `tomorrow-plan`: build a structured next-day plan from normalized daily inputs.
- `holding-analysis`: load stock bars and build a support, resistance, trend, and risk-action plan.

Core boundaries:

- Read-only research only. No broker or order tools are registered.
- Daily tasks fail on data-quality errors and degrade explicitly on allowed warnings.
- Holding analysis requires a symbol and positive holding cost.
- Domain conclusions remain deterministic and testable.

CLI examples:

```powershell
python tools\run_research_agent.py tomorrow-plan --date 2026-06-04 --allow-quality-warnings --offline
python tools\run_research_agent.py post-market-review --date 2026-06-04 --allow-quality-warnings --offline
python tools\run_research_agent.py holding-analysis --symbol 600580.SH --name 卧龙电驱 --cost 42.5 --position-pct 60
```
