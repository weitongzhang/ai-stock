"""Deterministic metrics for Harness evaluation results."""

from __future__ import annotations

from collections import Counter

from skill_lab.shared.enums import EvalErrorType
from skill_lab.shared.schemas import EvalReport, EvalResult


def pass_rate(results: list[EvalResult]) -> float:
    if not results:
        return 0.0
    return sum(1 for result in results if result.passed) / len(results)


def average_score(results: list[EvalResult]) -> float:
    if not results:
        return 0.0
    return sum(result.score for result in results) / len(results)


def error_counts(results: list[EvalResult]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for result in results:
        for error_type in result.error_types:
            if isinstance(error_type, EvalErrorType):
                counter[error_type.value] += 1
            else:
                counter[str(error_type)] += 1
    return dict(counter)


def build_report(
    results: list[EvalResult],
    target_version: str = "",
    judge_version: str = "",
) -> EvalReport:
    domain = results[0].domain if results else None
    if domain is None:
        raise ValueError("Cannot build an EvalReport without at least one result.")
    return EvalReport(
        domain=domain,
        target_version=target_version,
        judge_version=judge_version,
        total=len(results),
        passed=sum(1 for result in results if result.passed),
        avg_score=round(average_score(results), 4),
        error_counts=error_counts(results),
        results=results,
    )

