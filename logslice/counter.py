"""Running counters and rate tracking for log record streams."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, Optional


@dataclass
class Counter:
    """Mutable counter that tracks total and per-field-value tallies."""

    total: int = 0
    by_value: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def increment(self, value: Optional[str] = None) -> None:
        self.total += 1
        key = str(value) if value is not None else "<null>"
        self.by_value[key] += 1

    def reset(self) -> None:
        self.total = 0
        self.by_value.clear()


def count_records(
    records: Iterable[dict],
    field: Optional[str] = None,
) -> Counter:
    """Consume *records* and return a populated Counter.

    If *field* is given the counter also tracks per-value tallies for that
    field; otherwise every record is bucketed under ``<null>``.
    """
    counter = Counter()
    for record in records:
        value = record.get(field) if field else None
        counter.increment(value)
    return counter


def count_stream(
    records: Iterable[dict],
    field: Optional[str] = None,
    *,
    checkpoint: int = 0,
) -> Iterator[dict]:
    """Pass records through unchanged while maintaining a running count.

    Yields each record unmodified.  If *checkpoint* > 0 a summary record is
    injected every *checkpoint* records with ``_logslice_count`` set to the
    running total so far.
    """
    if checkpoint < 0:
        raise ValueError("checkpoint must be >= 0")

    counter = Counter()
    for record in records:
        value = record.get(field) if field else None
        counter.increment(value)
        yield record
        if checkpoint and counter.total % checkpoint == 0:
            yield {"_logslice_count": counter.total, "_logslice_checkpoint": True}
