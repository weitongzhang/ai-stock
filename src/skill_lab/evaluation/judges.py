"""Judge interfaces for the Trading Research Harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from skill_lab.shared.enums import EvalErrorType
from skill_lab.shared.schemas import EvalResult, EvalSample


class Judge(Protocol):
    """Protocol implemented by code judges and agent-backed judges."""

    name: str
    version: str

    def evaluate(self, sample: EvalSample) -> EvalResult:
        """Evaluate a single sample."""


@dataclass(slots=True)
class RequiredFieldJudge:
    """Deterministic judge that checks required output fields."""

    required_fields: list[str]
    name: str = "required_field_judge"
    version: str = "0.1.0"

    def evaluate(self, sample: EvalSample) -> EvalResult:
        output = sample.input_data.get("output")
        format_ok = isinstance(output, dict)
        missing = []
        if format_ok:
            missing = [field for field in self.required_fields if field not in output]
        field_complete = format_ok and not missing
        errors: list[EvalErrorType] = []
        if not format_ok:
            errors.append(EvalErrorType.FORMAT_ERROR)
        if missing:
            errors.append(EvalErrorType.MISSING_FIELD)
        score = 100.0 if field_complete else max(0.0, 100.0 - len(errors) * 40.0)
        return EvalResult(
            sample_id=sample.sample_id,
            domain=sample.domain,
            judge_version=self.version,
            format_ok=format_ok,
            field_complete=field_complete,
            score=score,
            passed=field_complete,
            error_types=errors,
            notes="missing=" + ",".join(missing) if missing else "",
        )


def agent_judge_prompt(domain: str) -> str:
    """Return the reusable prompt skeleton for future specialized judge agents."""

    return f"""You are a professional evaluation agent for {domain}.

Your task is not to provide investment advice. Your task is to evaluate whether
the system output follows the domain methodology and evidence standard.

Input includes:
- raw data
- system output
- ground truth or delayed outcome
- current evaluation plan

Workflow:
1. Check output format and required fields.
2. Check whether evidence supports the conclusion.
3. Check whether the output is overconfident.
4. Check whether confirmation and invalidation conditions are clear.
5. Score by the rubric.
6. Assign error types.
7. Return valid JSON only.
"""

