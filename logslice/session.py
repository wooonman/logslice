"""Session tracking: group correlated record groups into named sessions."""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional


def label_sessions(
    groups: Iterable[List[dict]],
    *,
    session_field: str = "session_id",
    prefix: str = "sess",
    start: int = 1,
) -> Iterator[List[dict]]:
    """Attach a monotonically increasing *session_field* to every record in
    each group and yield the annotated group.
    """
    for idx, group in enumerate(groups, start=start):
        sid = f"{prefix}-{idx:06d}"
        labelled = [{**rec, session_field: sid} for rec in group]
        yield labelled


def flatten_sessions(
    groups: Iterable[List[dict]],
) -> Iterator[dict]:
    """Flatten a stream of groups back into individual records."""
    for group in groups:
        yield from group


def session_stats(
    groups: Iterable[List[dict]],
    *,
    timestamp_field: str = "ts",
) -> Iterator[dict]:
    """Yield a summary dict for each group containing size and duration."""
    for group in groups:
        size = len(group)
        ts_values: List[float] = []
        for rec in group:
            val = rec.get(timestamp_field)
            try:
                ts_values.append(float(val))  # type: ignore[arg-type]
            except (TypeError, ValueError):
                pass

        duration: Optional[float] = None
        if len(ts_values) >= 2:
            duration = max(ts_values) - min(ts_values)

        first = group[0] if group else {}
        yield {
            "size": size,
            "duration": duration,
            "first_ts": min(ts_values) if ts_values else None,
            "last_ts": max(ts_values) if ts_values else None,
            "sample": first,
        }
