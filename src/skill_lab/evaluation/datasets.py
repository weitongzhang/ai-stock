"""Dataset helpers for Harness samples."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from skill_lab.shared.enums import EvalDomain
from skill_lab.shared.schemas import EvalSample
from skill_lab.shared.serialization import parse_enum


def load_jsonl(path: Path) -> list[EvalSample]:
    samples: list[EvalSample] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            data = json.loads(line)
            samples.append(sample_from_dict(data))
    return samples


def load_csv(path: Path) -> list[EvalSample]:
    samples: list[EvalSample] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            data: dict[str, Any] = dict(row)
            samples.append(sample_from_dict(data))
    return samples


def sample_from_dict(data: dict[str, Any]) -> EvalSample:
    input_data = data.get("input_data")
    if isinstance(input_data, str):
        input_data = json.loads(input_data)
    ground_truth = data.get("ground_truth")
    if isinstance(ground_truth, str) and ground_truth.strip():
        ground_truth = json.loads(ground_truth)
    return EvalSample(
        sample_id=str(data.get("sample_id", "")),
        domain=parse_enum(EvalDomain, data.get("domain"), EvalDomain.DAILY_REVIEW),
        input_data=dict(input_data or {}),
        ground_truth=dict(ground_truth or {}),
        meta=dict(data.get("meta") or {}),
    )

