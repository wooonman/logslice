"""Field-level profiling: compute basic statistics over a stream of records."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, Iterable, List


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def profile_field(records: Iterable[dict], field: str) -> dict:
    """Return a stats dict for *field* across all records."""
    values: List[float] = []
    missing = 0
    type_counts: Counter = Counter()
    top: Counter = Counter()

    for rec in records:
        raw = rec.get(field)
        if raw is None:
            missing += 1
            continue
        type_counts[type(raw).__name__] += 1
        top[str(raw)] += 1
        n = _numeric(raw)
        if n is not None:
            values.append(n)

    total = missing + sum(type_counts.values())
    result: dict = {
        "field": field,
        "total": total,
        "present": total - missing,
        "missing": missing,
        "types": dict(type_counts),
        "top_values": [v for v, _ in top.most_common(5)],
    }

    if values:
        result["numeric"] = _numeric_stats(values)

    return result


def _numeric_stats(values: List[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    sorted_v = sorted(values)
    return {
        "count": n,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "mean": round(mean, 6),
        "stddev": round(math.sqrt(variance), 6),
        "median": _median(sorted_v),
    }


def _median(sorted_values: List[float]) -> float:
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2
    return sorted_values[mid]


def profile_all(records: Iterable[dict], fields: List[str] | None = None) -> List[dict]:
    """Profile every field found in the stream (or a specific list)."""
    rows = list(records)
    if fields is None:
        seen: dict = {}
        for rec in rows:
            for k in rec:
                seen[k] = True
        fields = list(seen)
    return [profile_field(rows, f) for f in fields]
