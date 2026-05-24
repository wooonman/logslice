"""Deduplicate log records based on one or more field values."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Iterator, List, Optional


def _make_key(record: dict, fields: List[str]) -> tuple:
    """Build a hashable key from the given fields in a record."""
    return tuple(record.get(f) for f in fields)


def dedup_by(
    records: Iterable[dict],
    fields: List[str],
    window: Optional[int] = None,
) -> Iterator[dict]:
    """Yield records that are unique with respect to *fields*.

    Parameters
    ----------
    records:
        Input stream of parsed JSON log records.
    fields:
        Field names whose combined value determines uniqueness.
    window:
        If given, only remember the last *window* distinct keys so memory
        usage stays bounded for long-running streams.  ``None`` means
        remember every key seen (safe for finite inputs).
    """
    if not fields:
        raise ValueError("fields must not be empty")
    if window is not None and window < 1:
        raise ValueError("window must be a positive integer")

    seen: OrderedDict[tuple, None] = OrderedDict()

    for record in records:
        key = _make_key(record, fields)
        if key in seen:
            if window is not None:
                # Move to end to mark as recently seen
                seen.move_to_end(key)
            continue
        seen[key] = None
        if window is not None and len(seen) > window:
            seen.popitem(last=False)
        yield record


def dedup_exact(
    records: Iterable[dict],
    window: Optional[int] = None,
) -> Iterator[dict]:
    """Yield records that are unique across *all* their fields.

    This is a convenience wrapper around :func:`dedup_by` that derives the
    field list from the first record seen.
    """
    peekable = iter(records)
    first = next(peekable, None)
    if first is None:
        return

    fields = list(first.keys())
    from itertools import chain
    yield from dedup_by(chain([first], peekable), fields=fields, window=window)
