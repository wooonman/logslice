"""Merge multiple sorted log record streams into a single time-ordered stream."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator


_MISSING = object()


def _get_timestamp(record: dict, field: str) -> str | None:
    """Return the timestamp value for a record, or None if missing."""
    val = record.get(field)
    return str(val) if val is not None else None


def merge_sorted(
    streams: Iterable[Iterable[dict]],
    key: str = "timestamp",
) -> Iterator[dict]:
    """Merge multiple pre-sorted streams into one sorted stream.

    Records without the key field sort before those that have it.
    """
    # heap entries: (sort_key, stream_index, record)
    heap: list[tuple[tuple, int, dict]] = []

    iters = [iter(s) for s in streams]

    for idx, it in enumerate(iters):
        try:
            record = next(it)
            ts = _get_timestamp(record, key)
            sort_key = (0, ts) if ts is None else (1, ts)
            heapq.heappush(heap, (sort_key, idx, record))
        except StopIteration:
            pass

    while heap:
        sort_key, idx, record = heapq.heappop(heap)
        yield record
        try:
            next_record = next(iters[idx])
            ts = _get_timestamp(next_record, key)
            next_key = (0, ts) if ts is None else (1, ts)
            heapq.heappush(heap, (next_key, idx, next_record))
        except StopIteration:
            pass


def merge_unordered(
    streams: Iterable[Iterable[dict]],
) -> Iterator[dict]:
    """Interleave multiple streams without any sorting guarantee."""
    for stream in streams:
        yield from stream


def merge(
    streams: Iterable[Iterable[dict]],
    key: str | None = "timestamp",
) -> Iterator[dict]:
    """Merge streams. If key is set, output is sorted by that field."""
    if key:
        return merge_sorted(streams, key=key)
    return merge_unordered(streams)
