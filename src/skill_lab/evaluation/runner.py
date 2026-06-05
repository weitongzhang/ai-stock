"""Small runner utilities for Harness judges."""

from __future__ import annotations

from skill_lab.evaluation.judges import Judge
from skill_lab.evaluation.metrics import build_report
from skill_lab.shared.schemas import EvalReport, EvalSample


def run_judge(
    judge: Judge,
    samples: list[EvalSample],
    target_version: str = "",
) -> EvalReport:
    results = [judge.evaluate(sample) for sample in samples]
    return build_report(
        results,
        target_version=target_version,
        judge_version=getattr(judge, "version", ""),
    )
