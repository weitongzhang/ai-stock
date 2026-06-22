# Minimal Auditable Research Loop

This example demonstrates a plan-to-outcome loop using the repository's existing
research controller, shared schemas, and append-only decision journal.

Run:

```powershell
python tools\run_audit_loop_example.py
```

Outputs are written to `examples/audit-loop/output/`:

- `decision-journal.jsonl`: append-only plan, outcome, and evaluation events.
- `audit-summary.json`: machine-readable closure report.
- `audit-summary.md`: human-readable audit report.

The next-day outcome is intentionally simulated. Production workflows should
replace it with observed market evidence or explicit human decisions.
