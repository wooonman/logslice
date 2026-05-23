"""Simple aggregation helpers for grouped log analysis."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

from logslice.query import _get_nested


def count_by(records: Iterable[dict], field: str) -> dict[str, int]:
    """Count records grouped by the value of *field*.

    Missing / None values are bucketed under the key ``"<null>"``.
    """
    counter: Counter = Counter()
    for record in records:
        value = _get_nested(record, field)
        key = str(value) if value is not None else "<null>"
        counter[key] += 1
    return dict(counter.most_common())


def collect_values(records: Iterable[dict], field: str) -> list[Any]:
    """Return a flat list of every value found at *field* across all records."""
    values: list[Any] = []
    for record in records:
        value = _get_nested(record, field)
        if value is not None:
            values.append(value)
    return values


def summarise(records: Iterable[dict], field: str) -> dict[str, Any]:
    """Return basic numeric statistics for a numeric *field*.

    Returns a dict with keys: count, min, max, sum, mean.
    Non-numeric values are silently skipped.
    """
    nums: list[float] = []
    for record in records:
        raw = _get_nested(record, field)
        try:
            nums.append(float(raw))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue

    if not nums:
        return {"count": 0, "min": None, "max": None, "sum": None, "mean": None}

    total = sum(nums)
    return {
        "count": len(nums),
        "min": min(nums),
        "max": max(nums),
        "sum": total,
        "mean": total / len(nums),
    }


def group_by(records: Iterable[dict], field: str) -> dict[str, list[dict]]:
    """Partition records into lists keyed by the string value of *field*."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        value = _get_nested(record, field)
        key = str(value) if value is not None else "<null>"
        groups[key].append(record)
    return dict(groups)
