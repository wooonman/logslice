"""Utilities for normalising and converting timestamp fields in log records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Iterator


_UNITS_TO_DIVISOR: dict[str, float] = {
    "s": 1.0,
    "ms": 1_000.0,
    "us": 1_000_000.0,
    "ns": 1_000_000_000.0,
}


def _to_datetime(value: object, unit: str = "s") -> datetime | None:
    """Convert a numeric epoch value to a UTC datetime, or return None on failure."""
    if not isinstance(value, (int, float)):
        return None
    divisor = _UNITS_TO_DIVISOR.get(unit, 1.0)
    try:
        return datetime.fromtimestamp(value / divisor, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


def normalise_timestamp(
    records: Iterable[dict],
    src_field: str = "timestamp",
    dst_field: str = "time",
    unit: str = "s",
    fmt: str = "%Y-%m-%dT%H:%M:%SZ",
) -> Iterator[dict]:
    """Add *dst_field* containing a formatted UTC string derived from *src_field*.

    Records where *src_field* is absent or cannot be converted are passed through
    unchanged.
    """
    for record in records:
        raw = record.get(src_field)
        dt = _to_datetime(raw, unit)
        if dt is not None:
            yield {**record, dst_field: dt.strftime(fmt)}
        else:
            yield record


def convert_to_epoch(
    records: Iterable[dict],
    src_field: str = "time",
    dst_field: str = "epoch",
    fmt: str = "%Y-%m-%dT%H:%M:%SZ",
) -> Iterator[dict]:
    """Add *dst_field* containing a UTC epoch (float) parsed from an ISO-like string.

    Records where *src_field* is absent or unparseable are passed through unchanged.
    """
    for record in records:
        raw = record.get(src_field)
        if not isinstance(raw, str):
            yield record
            continue
        try:
            dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            yield {**record, dst_field: dt.timestamp()}
        except ValueError:
            yield record
