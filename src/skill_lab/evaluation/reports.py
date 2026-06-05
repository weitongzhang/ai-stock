"""Report rendering for Harness evaluation outputs."""

from __future__ import annotations

from skill_lab.shared.schemas import EvalReport


def render_markdown(report: EvalReport) -> str:
    lines = [
        f"# Evaluation Report: {report.domain.value}",
        "",
        f"- Target version: {report.target_version or 'unknown'}",
        f"- Judge version: {report.judge_version or 'unknown'}",
        f"- Total samples: {report.total}",
        f"- Passed: {report.passed}",
        f"- Average score: {report.avg_score:.2f}",
        "",
        "## Error Counts",
        "",
    ]
    if report.error_counts:
        for key, value in sorted(report.error_counts.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none")
    lines.extend(["", "## Failed Samples", ""])
    failed = [result for result in report.results if not result.passed]
    if not failed:
        lines.append("- none")
    for result in failed:
        errors = ", ".join(error.value for error in result.error_types)
        lines.append(f"- {result.sample_id}: {errors or 'unknown'}; {result.notes}")
    return "\n".join(lines)

