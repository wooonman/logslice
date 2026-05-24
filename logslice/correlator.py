"""Correlate log records by a shared field value within a time window."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional


def correlate(
    records: Iterable[dict],
    field: str,
    *,
    timestamp_field: str = "ts",
    window: float = 5.0,
) -> Iterator[List[dict]]:
    """Group records that share the same *field* value and fall within
    *window* seconds of the first record seen for that value.

    Yields a list (group) once no new record arrives for that key within
    the window, determined by the monotonically increasing timestamp of
    subsequent records from *other* keys.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    bucket_start: Dict[str, float] = {}

    for record in records:
        key = record.get(field)
        if key is None:
            continue

        ts = _ts(record, timestamp_field)

        # flush buckets whose window has expired relative to current ts
        expired = [
            k
            for k, start in bucket_start.items()
            if k != key and ts is not None and ts - start > window
        ]
        for k in expired:
            yield buckets.pop(k)
            del bucket_start[k]

        if key not in bucket_start:
            bucket_start[key] = ts if ts is not None else 0.0

        buckets[key].append(record)

    # flush remaining
    for k in list(buckets):
        yield buckets.pop(k)


def correlate_exact(
    records: Iterable[dict],
    field: str,
    expected: int,
) -> Iterator[List[dict]]:
    """Collect records that share *field* and yield once *expected* members
    are gathered.  Incomplete groups are yielded at exhaustion.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)

    for record in records:
        key = record.get(field)
        if key is None:
            continue
        buckets[key].append(record)
        if len(buckets[key]) >= expected:
            yield buckets.pop(key)

    for group in buckets.values():
        if group:
            yield group


def _ts(record: dict, field: str) -> Optional[float]:
    val = record.get(field)
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
